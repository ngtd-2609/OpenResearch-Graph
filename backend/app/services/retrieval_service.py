from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import numpy as np
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import DocumentChunk
from app.services.embedding_service import get_embedding_service
from app.services.reranking_service import get_reranking_service


@dataclass(slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    vector_score: float
    keyword_score: float
    rerank_score: float
    final_score: float
    embedding: list[float]


class RetrievalService:
    """Hybrid pgvector/full-text retrieval with a portable Python fallback."""

    async def retrieve(
        self,
        db: AsyncSession,
        *,
        document_id: UUID,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        requested_top_k = top_k or settings.rag_top_k
        candidate_limit = max(settings.rag_candidate_pool, requested_top_k * 3)
        query_vector = get_embedding_service().encode_query(query)

        candidates = await self._database_candidates(
            db,
            document_id=document_id,
            query=query,
            query_vector=query_vector,
            limit=candidate_limit,
        )
        if not candidates:
            candidates = await self._python_candidates(
                db,
                document_id=document_id,
                query=query,
                query_vector=query_vector,
                limit=candidate_limit,
            )
        if not candidates:
            return []

        rerank_scores = get_reranking_service().score(
            query,
            [candidate.chunk.content for candidate in candidates],
        )
        for candidate, rerank_score in zip(candidates, rerank_scores, strict=True):
            candidate.rerank_score = rerank_score
            candidate.final_score = (
                0.50 * candidate.vector_score
                + 0.20 * candidate.keyword_score
                + 0.30 * rerank_score
            )

        return self._mmr_select(
            candidates,
            top_k=requested_top_k,
            diversity_lambda=settings.rag_mmr_lambda,
        )

    async def _database_candidates(
        self,
        db: AsyncSession,
        *,
        document_id: UUID,
        query: str,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        bind = db.get_bind()
        if bind.dialect.name != "postgresql" or not hasattr(DocumentChunk.embedding, "cosine_distance"):
            return []

        merged: dict[UUID, RetrievedChunk] = {}
        try:
            distance = DocumentChunk.embedding.cosine_distance(query_vector)
            vector_stmt = (
                select(DocumentChunk, (1.0 - distance).label("vector_score"))
                .where(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.embedding.is_not(None),
                )
                .order_by(distance)
                .limit(limit)
            )
            for chunk, score in (await db.execute(vector_stmt)).all():
                embedding = list(chunk.embedding or [])
                merged[chunk.id] = RetrievedChunk(
                    chunk=chunk,
                    vector_score=max(0.0, min(1.0, float(score or 0.0))),
                    keyword_score=0.0,
                    rerank_score=0.0,
                    final_score=0.0,
                    embedding=embedding,
                )

            ts_query = func.plainto_tsquery("simple", query)
            text_vector = func.to_tsvector("simple", DocumentChunk.content)
            rank = func.ts_rank_cd(text_vector, ts_query)
            keyword_stmt = (
                select(DocumentChunk, rank.label("keyword_score"))
                .where(
                    DocumentChunk.document_id == document_id,
                    text_vector.op("@@")(ts_query),
                )
                .order_by(rank.desc())
                .limit(limit)
            )
            for chunk, score in (await db.execute(keyword_stmt)).all():
                item = merged.get(chunk.id)
                if item is None:
                    embedding = list(chunk.embedding or get_embedding_service().encode_query(chunk.content))
                    item = RetrievedChunk(
                        chunk=chunk,
                        vector_score=get_embedding_service().cosine_similarity(
                            query_vector,
                            embedding,
                        ),
                        keyword_score=0.0,
                        rerank_score=0.0,
                        final_score=0.0,
                        embedding=embedding,
                    )
                    merged[chunk.id] = item
                item.keyword_score = max(0.0, min(1.0, float(score or 0.0)))
        except SQLAlchemyError:
            return []
        return list(merged.values())

    async def _python_candidates(
        self,
        db: AsyncSession,
        *,
        document_id: UUID,
        query: str,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        chunks = list(
            (
                await db.scalars(
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == document_id)
                    .order_by(DocumentChunk.chunk_index)
                    .limit(2_000)
                )
            ).all()
        )
        query_terms = set(query.lower().split())
        candidates: list[RetrievedChunk] = []
        for chunk in chunks:
            embedding = list(chunk.embedding or get_embedding_service().encode_query(chunk.content))
            vector_score = get_embedding_service().cosine_similarity(query_vector, embedding)
            chunk_terms = set(chunk.content.lower().split())
            keyword_score = len(query_terms & chunk_terms) / max(len(query_terms), 1)
            candidates.append(
                RetrievedChunk(
                    chunk=chunk,
                    vector_score=max(0.0, vector_score),
                    keyword_score=keyword_score,
                    rerank_score=0.0,
                    final_score=0.0,
                    embedding=embedding,
                )
            )
        candidates.sort(
            key=lambda item: 0.7 * item.vector_score + 0.3 * item.keyword_score,
            reverse=True,
        )
        return candidates[:limit]

    @staticmethod
    def _mmr_select(
        candidates: list[RetrievedChunk],
        *,
        top_k: int,
        diversity_lambda: float,
    ) -> list[RetrievedChunk]:
        remaining = sorted(candidates, key=lambda item: item.final_score, reverse=True)
        selected: list[RetrievedChunk] = []
        while remaining and len(selected) < top_k:
            best_index = 0
            best_score = float("-inf")
            for index, candidate in enumerate(remaining):
                if not selected:
                    mmr_score = candidate.final_score
                else:
                    diversity_penalty = max(
                        float(
                            np.dot(
                                np.asarray(candidate.embedding, dtype=np.float32),
                                np.asarray(item.embedding, dtype=np.float32),
                            )
                        )
                        for item in selected
                    )
                    mmr_score = (
                        diversity_lambda * candidate.final_score
                        - (1.0 - diversity_lambda) * diversity_penalty
                    )
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_index = index
            selected.append(remaining.pop(best_index))
        return selected
