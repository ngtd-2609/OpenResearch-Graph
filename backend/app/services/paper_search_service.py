from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import exists, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import (
    Author,
    Institution,
    Paper,
    PaperAuthor,
    PaperInstitution,
    PaperTopic,
    Topic,
)
from app.services.embedding_service import get_embedding_service
from app.services.reranking_service import get_reranking_service

TOKEN_PATTERN = re.compile(r"[\w-]+", re.UNICODE)


@dataclass(slots=True)
class PaperSearchFilters:
    from_year: int | None = None
    to_year: int | None = None
    open_access: bool | None = None
    author: str | None = None
    institution: str | None = None
    topic: str | None = None
    paper_type: str | None = None


@dataclass(slots=True)
class ScoredPaper:
    paper: Paper
    score: float
    components: dict[str, float]


class PaperSearchService:
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        filters: PaperSearchFilters,
        page: int,
        per_page: int,
    ) -> tuple[int, list[Paper]]:
        conditions = self._conditions(filters)
        total = int(
            await db.scalar(select(func.count()).select_from(Paper).where(*conditions)) or 0
        )
        query_vector = get_embedding_service().encode_query(query)
        candidate_pool = max(settings.search_candidate_pool, page * per_page * 3)
        candidates = await self._database_candidates(
            db,
            query=query,
            query_vector=query_vector,
            conditions=conditions,
            limit=candidate_pool,
        )
        if not candidates:
            candidates = list(
                (
                    await db.scalars(
                        select(Paper)
                        .where(*conditions)
                        .order_by(Paper.cited_by_count.desc())
                        .limit(candidate_pool)
                    )
                ).all()
            )
        ranked = self._rank(query, query_vector, candidates)
        offset = (page - 1) * per_page
        return total, [item.paper for item in ranked[offset : offset + per_page]]

    def _conditions(self, filters: PaperSearchFilters) -> list[object]:
        conditions: list[object] = []
        if filters.from_year is not None:
            conditions.append(Paper.publication_year >= filters.from_year)
        if filters.to_year is not None:
            conditions.append(Paper.publication_year <= filters.to_year)
        if filters.open_access is not None:
            conditions.append(Paper.is_open_access == filters.open_access)
        if filters.paper_type:
            conditions.append(Paper.type == filters.paper_type)
        if filters.author:
            conditions.append(
                exists(
                    select(PaperAuthor.paper_id)
                    .join(Author, Author.id == PaperAuthor.author_id)
                    .where(
                        PaperAuthor.paper_id == Paper.id,
                        Author.name.ilike(f"%{filters.author}%"),
                    )
                )
            )
        if filters.institution:
            conditions.append(
                exists(
                    select(PaperInstitution.paper_id)
                    .join(Institution, Institution.id == PaperInstitution.institution_id)
                    .where(
                        PaperInstitution.paper_id == Paper.id,
                        Institution.name.ilike(f"%{filters.institution}%"),
                    )
                )
            )
        if filters.topic:
            conditions.append(
                exists(
                    select(PaperTopic.paper_id)
                    .join(Topic, Topic.id == PaperTopic.topic_id)
                    .where(
                        PaperTopic.paper_id == Paper.id,
                        Topic.name.ilike(f"%{filters.topic}%"),
                    )
                )
            )
        return conditions

    async def _database_candidates(
        self,
        db: AsyncSession,
        *,
        query: str,
        query_vector: list[float],
        conditions: list[object],
        limit: int,
    ) -> list[Paper]:
        bind = db.get_bind()
        if bind.dialect.name != "postgresql":
            lexical = or_(Paper.title.ilike(f"%{query}%"), Paper.abstract.ilike(f"%{query}%"))
            return list(
                (
                    await db.scalars(
                        select(Paper)
                        .where(*conditions, lexical)
                        .order_by(Paper.cited_by_count.desc())
                        .limit(limit)
                    )
                ).all()
            )

        merged: dict[object, Paper] = {}
        try:
            text_vector = func.to_tsvector(
                "simple",
                func.concat_ws(" ", Paper.title, func.coalesce(Paper.abstract, "")),
            )
            ts_query = func.websearch_to_tsquery("simple", query)
            keyword_stmt = (
                select(Paper)
                .where(*conditions, text_vector.op("@@")(ts_query))
                .order_by(func.ts_rank_cd(text_vector, ts_query).desc())
                .limit(limit)
            )
            for paper in (await db.scalars(keyword_stmt)).all():
                merged[paper.id] = paper

            if hasattr(Paper.embedding, "cosine_distance"):
                distance = Paper.embedding.cosine_distance(query_vector)
                vector_stmt = (
                    select(Paper)
                    .where(*conditions, Paper.embedding.is_not(None))
                    .order_by(distance)
                    .limit(limit)
                )
                for paper in (await db.scalars(vector_stmt)).all():
                    merged[paper.id] = paper
        except SQLAlchemyError:
            return []
        return list(merged.values())

    def _rank(
        self,
        query: str,
        query_vector: list[float],
        papers: list[Paper],
    ) -> list[ScoredPaper]:
        if not papers:
            return []
        embedding_service = get_embedding_service()
        missing = [paper for paper in papers if not paper.embedding]
        generated = embedding_service.encode(
            [f"{paper.title} {paper.abstract or ''}" for paper in missing]
        )
        generated_by_id = {
            paper.id: vector for paper, vector in zip(missing, generated, strict=True)
        }
        max_citations = max((paper.cited_by_count for paper in papers), default=1)
        current_year = datetime.now(UTC).year
        terms = set(TOKEN_PATTERN.findall(query.lower()))
        weights = settings.search_weights
        prelim: list[ScoredPaper] = []
        for paper in papers:
            paper_text = f"{paper.title} {paper.abstract or ''}"
            vector = list(paper.embedding or generated_by_id[paper.id])
            semantic = max(0.0, embedding_service.cosine_similarity(query_vector, vector))
            paper_terms = set(TOKEN_PATTERN.findall(paper_text.lower()))
            keyword = len(terms & paper_terms) / max(len(terms), 1)
            citation = math.log1p(max(paper.cited_by_count, 0)) / max(
                math.log1p(max_citations),
                1.0,
            )
            age = max(0, current_year - (paper.publication_year or current_year))
            recency = math.exp(-age / 8.0)
            access = 1.0 if paper.is_open_access else 0.0
            base_score = (
                weights["keyword"] * keyword
                + weights["semantic"] * semantic
                + weights["citation"] * citation
                + weights["recency"] * recency
                + weights["open_access"] * access
            )
            prelim.append(
                ScoredPaper(
                    paper=paper,
                    score=base_score,
                    components={
                        "keyword": keyword,
                        "semantic": semantic,
                        "citation": citation,
                        "recency": recency,
                        "open_access": access,
                        "rerank": 0.0,
                    },
                )
            )

        prelim.sort(key=lambda item: item.score, reverse=True)
        rerank_count = min(15, len(prelim))
        if rerank_count > 0 and weights.get("rerank", 0) > 0:
            rerank_scores = get_reranking_service().score(
                query,
                [f"{item.paper.title} {item.paper.abstract or ''}" for item in prelim[:rerank_count]],
            )
            for item, rerank_score in zip(prelim[:rerank_count], rerank_scores, strict=True):
                item.components["rerank"] = rerank_score
                item.score += weights["rerank"] * rerank_score
        return sorted(prelim, key=lambda item: item.score, reverse=True)
