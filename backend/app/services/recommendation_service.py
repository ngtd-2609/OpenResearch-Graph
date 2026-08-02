from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import networkx as nx
import numpy as np
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.entities import Citation, LibraryItem, Paper, UserPaperInteraction
from app.services.embedding_service import get_embedding_service

INTERACTION_WEIGHTS: dict[str, float] = {
    "view": 0.15,
    "click": 0.25,
    "chat": 0.35,
    "download": 0.60,
    "save": 1.00,
    "like": 1.20,
    "share": 0.70,
    "cite": 1.40,
    "unsave": -0.50,
    "dislike": -1.20,
    "dismiss": -1.00,
}
NEGATIVE_INTERACTIONS = {"dislike", "dismiss"}


@dataclass(slots=True)
class Recommendation:
    paper: Paper
    score: float
    explanation: str
    components: dict[str, float]


class RecommendationService:
    """Hybrid recommender using content, collaborative and citation-graph signals."""

    async def recommend(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
    ) -> list[Recommendation]:
        library_items = list(
            (
                await db.scalars(
                    select(LibraryItem)
                    .options(selectinload(LibraryItem.paper))
                    .where(LibraryItem.user_id == user_id)
                )
            ).all()
        )
        user_interactions = list(
            (
                await db.scalars(
                    select(UserPaperInteraction).where(
                        UserPaperInteraction.user_id == user_id
                    )
                )
            ).all()
        )
        profile_weights = self._profile_weights(library_items, user_interactions)
        excluded_ids = {item.paper_id for item in library_items}
        excluded_ids.update(
            interaction.paper_id
            for interaction in user_interactions
            if interaction.interaction_type in NEGATIVE_INTERACTIONS
        )

        candidates = list(
            (
                await db.scalars(
                    select(Paper)
                    .order_by(desc(Paper.cited_by_count))
                    .limit(settings.recommendation_candidate_pool)
                )
            ).all()
        )
        candidates = [paper for paper in candidates if paper.id not in excluded_ids]
        if not candidates:
            return []

        profile_paper_ids = set(profile_weights)
        profile_papers = {
            item.paper.id: item.paper
            for item in library_items
            if item.paper is not None
        }
        missing_profile_ids = profile_paper_ids - set(profile_papers)
        if missing_profile_ids:
            rows = list(
                (
                    await db.scalars(
                        select(Paper).where(Paper.id.in_(missing_profile_ids))
                    )
                ).all()
            )
            profile_papers.update({paper.id: paper for paper in rows})

        vector_by_id = self._paper_vectors(candidates + list(profile_papers.values()))
        profile_vector = self._build_profile_vector(profile_weights, vector_by_id)
        collaborative_scores = await self._collaborative_scores(
            db,
            user_id=user_id,
            positive_paper_ids={
                paper_id for paper_id, weight in profile_weights.items() if weight > 0
            },
            candidate_ids={paper.id for paper in candidates},
        )
        graph_scores = await self._graph_scores(
            db,
            candidate_ids={paper.id for paper in candidates},
            seed_ids={paper_id for paper_id, weight in profile_weights.items() if weight > 0},
        )

        max_citations = max((paper.cited_by_count for paper in candidates), default=1)
        current_year = datetime.now(UTC).year
        feedback_by_paper = self._latest_feedback(user_interactions)
        scored: list[Recommendation] = []
        for paper in candidates:
            vector = vector_by_id[paper.id]
            content = (
                max(0.0, get_embedding_service().cosine_similarity(profile_vector, vector))
                if profile_vector is not None
                else 0.0
            )
            collaborative = collaborative_scores.get(paper.id, 0.0)
            graph = graph_scores.get(paper.id, 0.0)
            popularity = math.log1p(max(paper.cited_by_count, 0)) / max(
                math.log1p(max_citations),
                1.0,
            )
            age = max(0, current_year - (paper.publication_year or current_year))
            recency = math.exp(-age / 8.0)
            open_access = 1.0 if paper.is_open_access else 0.0
            feedback = max(
                0.0,
                INTERACTION_WEIGHTS.get(feedback_by_paper.get(paper.id, ""), 0.0),
            )
            components = {
                "content": content,
                "collaborative": collaborative,
                "graph": graph,
                "popularity": popularity,
                "recency": recency,
                "open_access": open_access,
                "feedback": feedback,
            }
            score = self._weighted_score(components)
            scored.append(
                Recommendation(
                    paper=paper,
                    score=round(score, 4),
                    explanation=self._explain(components, cold_start=profile_vector is None),
                    components={name: round(value, 4) for name, value in components.items()},
                )
            )

        return self._diversified_top_k(scored, vector_by_id, limit)

    @staticmethod
    def _profile_weights(
        library_items: list[LibraryItem],
        interactions: list[UserPaperInteraction],
    ) -> dict[UUID, float]:
        weights: defaultdict[UUID, float] = defaultdict(float)
        for item in library_items:
            weights[item.paper_id] += INTERACTION_WEIGHTS["save"]
        for interaction in interactions:
            base = INTERACTION_WEIGHTS.get(interaction.interaction_type, 0.0)
            weights[interaction.paper_id] += base * interaction.interaction_value
        return dict(weights)

    @staticmethod
    def _latest_feedback(interactions: list[UserPaperInteraction]) -> dict[UUID, str]:
        ordered = sorted(interactions, key=lambda item: item.created_at)
        return {item.paper_id: item.interaction_type for item in ordered}

    @staticmethod
    def _paper_vectors(papers: list[Paper]) -> dict[UUID, list[float]]:
        unique = {paper.id: paper for paper in papers}
        missing = [paper for paper in unique.values() if not paper.embedding]
        generated = get_embedding_service().encode(
            [f"{paper.title} {paper.abstract or ''}" for paper in missing]
        )
        generated_by_id = {
            paper.id: vector for paper, vector in zip(missing, generated, strict=True)
        }
        return {
            paper.id: list(paper.embedding or generated_by_id[paper.id])
            for paper in unique.values()
        }

    @staticmethod
    def _build_profile_vector(
        weights: dict[UUID, float],
        vector_by_id: dict[UUID, list[float]],
    ) -> list[float] | None:
        weighted_vectors: list[np.ndarray] = []
        positive_weights: list[float] = []
        for paper_id, weight in weights.items():
            if weight <= 0 or paper_id not in vector_by_id:
                continue
            weighted_vectors.append(np.asarray(vector_by_id[paper_id], dtype=np.float32) * weight)
            positive_weights.append(weight)
        if not weighted_vectors:
            return None
        profile = np.sum(weighted_vectors, axis=0) / max(sum(positive_weights), 1e-8)
        norm = float(np.linalg.norm(profile)) or 1.0
        return (profile / norm).astype(float).tolist()

    async def _collaborative_scores(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        positive_paper_ids: set[UUID],
        candidate_ids: set[UUID],
    ) -> dict[UUID, float]:
        if not positive_paper_ids:
            return {}
        overlap_rows = list(
            (
                await db.scalars(
                    select(UserPaperInteraction).where(
                        UserPaperInteraction.user_id != user_id,
                        UserPaperInteraction.paper_id.in_(positive_paper_ids),
                        UserPaperInteraction.interaction_type.in_(
                            ["save", "like", "download", "cite", "chat"]
                        ),
                    )
                )
            ).all()
        )
        similarity: defaultdict[UUID, float] = defaultdict(float)
        for row in overlap_rows:
            similarity[row.user_id] += max(
                0.0,
                INTERACTION_WEIGHTS.get(row.interaction_type, 0.0) * row.interaction_value,
            )
        similar_users = {
            user: score
            for user, score in sorted(
                similarity.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:100]
        }
        if not similar_users:
            return {}
        rows = list(
            (
                await db.scalars(
                    select(UserPaperInteraction).where(
                        UserPaperInteraction.user_id.in_(similar_users),
                        UserPaperInteraction.paper_id.in_(candidate_ids),
                    )
                )
            ).all()
        )
        scores: defaultdict[UUID, float] = defaultdict(float)
        for row in rows:
            interaction_weight = INTERACTION_WEIGHTS.get(row.interaction_type, 0.0)
            if interaction_weight > 0:
                scores[row.paper_id] += (
                    similar_users[row.user_id] * interaction_weight * row.interaction_value
                )
        return self._normalize(scores)

    async def _graph_scores(
        self,
        db: AsyncSession,
        *,
        candidate_ids: set[UUID],
        seed_ids: set[UUID],
    ) -> dict[UUID, float]:
        graph_ids = candidate_ids | seed_ids
        if not graph_ids:
            return {}
        rows = (
            await db.execute(
                select(Citation.citing_paper_id, Citation.cited_paper_id).where(
                    Citation.citing_paper_id.in_(graph_ids),
                    Citation.cited_paper_id.in_(graph_ids),
                )
            )
        ).all()
        graph = nx.DiGraph()
        graph.add_nodes_from(graph_ids)
        graph.add_edges_from(rows)
        if not graph.number_of_edges():
            return {}
        personalization = None
        active_seeds = seed_ids & set(graph.nodes)
        if active_seeds:
            personalization = {
                node: (1.0 if node in active_seeds else 0.0) for node in graph.nodes
            }
        scores = nx.pagerank(graph, alpha=0.85, personalization=personalization)
        return self._normalize(
            {paper_id: score for paper_id, score in scores.items() if paper_id in candidate_ids}
        )

    @staticmethod
    def _normalize(values: dict[UUID, float]) -> dict[UUID, float]:
        if not values:
            return {}
        maximum = max(values.values())
        if maximum <= 0:
            return {key: 0.0 for key in values}
        return {key: value / maximum for key, value in values.items()}

    @staticmethod
    def _weighted_score(components: dict[str, float]) -> float:
        return (
            settings.recommendation_content_weight * components["content"]
            + settings.recommendation_collaborative_weight * components["collaborative"]
            + settings.recommendation_graph_weight * components["graph"]
            + settings.recommendation_popularity_weight * components["popularity"]
            + settings.recommendation_recency_weight * components["recency"]
            + settings.recommendation_open_access_weight * components["open_access"]
            + settings.recommendation_feedback_weight * components["feedback"]
        )

    @staticmethod
    def _explain(components: dict[str, float], *, cold_start: bool) -> str:
        if cold_start:
            reasons = ["phù hợp cho người dùng mới"]
        else:
            reasons = []
        ranked = sorted(components.items(), key=lambda item: item[1], reverse=True)
        labels = {
            "content": "nội dung tương tự thư viện của bạn",
            "collaborative": "người dùng có hành vi tương tự cũng quan tâm",
            "graph": "có vị trí tốt trong mạng trích dẫn",
            "popularity": "có ảnh hưởng trích dẫn cao",
            "recency": "được công bố gần đây",
            "open_access": "có bản Open Access",
            "feedback": "phù hợp với phản hồi trước đây của bạn",
        }
        reasons.extend(labels[name] for name, value in ranked if value >= 0.55)
        unique_reasons = list(dict.fromkeys(reasons))[:3]
        return "Được đề xuất vì " + ", ".join(unique_reasons or ["có điểm hybrid tổng hợp tốt"]) + "."

    @staticmethod
    def _diversified_top_k(
        items: list[Recommendation],
        vector_by_id: dict[UUID, list[float]],
        limit: int,
    ) -> list[Recommendation]:
        remaining = sorted(items, key=lambda item: item.score, reverse=True)
        selected: list[Recommendation] = []
        year_counts: defaultdict[int, int] = defaultdict(int)
        while remaining and len(selected) < limit:
            best_index = 0
            best_value = float("-inf")
            for index, item in enumerate(remaining):
                year = item.paper.publication_year or 0
                year_penalty = 0.08 * max(0, year_counts[year] - 2)
                if selected:
                    vector = vector_by_id[item.paper.id]
                    similarity = max(
                        get_embedding_service().cosine_similarity(
                            vector,
                            vector_by_id[chosen.paper.id],
                        )
                        for chosen in selected
                    )
                else:
                    similarity = 0.0
                mmr = (
                    settings.recommendation_diversity_lambda * item.score
                    - (1.0 - settings.recommendation_diversity_lambda) * similarity
                    - year_penalty
                )
                if mmr > best_value:
                    best_value = mmr
                    best_index = index
            chosen = remaining.pop(best_index)
            selected.append(chosen)
            year_counts[chosen.paper.publication_year or 0] += 1
        return selected
