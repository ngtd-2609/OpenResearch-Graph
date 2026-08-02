from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from app.models.entities import LibraryItem, Paper, UserPaperInteraction
from app.services.recommendation_service import RecommendationService


class Result:
    def __init__(self, rows: list[Any]) -> None:
        self.rows = rows

    def all(self) -> list[Any]:
        return self.rows


class FakeDb:
    def __init__(self, scalar_batches: list[list[Any]], graph_rows: list[tuple]) -> None:
        self.scalar_batches = scalar_batches
        self.graph_rows = graph_rows

    async def scalars(self, _statement: Any) -> Result:
        return Result(self.scalar_batches.pop(0))

    async def execute(self, _statement: Any) -> Result:
        return Result(self.graph_rows)


def paper(title: str, vector: list[float], *, citations: int, year: int, oa: bool = False) -> Paper:
    return Paper(
        id=uuid4(),
        title=title,
        abstract=f"Abstract for {title}",
        embedding=vector,
        cited_by_count=citations,
        publication_year=year,
        is_open_access=oa,
        referenced_works_count=0,
        metadata_json={},
    )


@pytest.mark.asyncio
async def test_hybrid_recommendation_executes_content_collaborative_and_graph_paths() -> None:
    user_id = uuid4()
    other_user = uuid4()
    seed = paper("Graph neural networks", [1.0, 0.0, 0.0], citations=20, year=2021)
    candidate_a = paper("Graph representation learning", [0.9, 0.1, 0.0], citations=50, year=2025, oa=True)
    candidate_b = paper("Classical optimization", [0.0, 1.0, 0.0], citations=100, year=2024)
    library = LibraryItem(
        id=uuid4(), user_id=user_id, paper_id=seed.id, collection_name="Saved", tags=[], paper=seed
    )
    own_like = UserPaperInteraction(
        id=uuid4(), user_id=user_id, paper_id=seed.id, interaction_type="like",
        interaction_value=1.0, created_at=datetime.now(UTC),
    )
    overlap = UserPaperInteraction(
        id=uuid4(), user_id=other_user, paper_id=seed.id, interaction_type="like",
        interaction_value=1.0, created_at=datetime.now(UTC),
    )
    related = UserPaperInteraction(
        id=uuid4(), user_id=other_user, paper_id=candidate_a.id, interaction_type="save",
        interaction_value=1.0, created_at=datetime.now(UTC),
    )
    db = FakeDb(
        scalar_batches=[
            [library],
            [own_like],
            [candidate_a, candidate_b],
            [overlap],
            [related],
        ],
        graph_rows=[(seed.id, candidate_a.id), (candidate_a.id, candidate_b.id)],
    )

    results = await RecommendationService().recommend(db, user_id, limit=2)  # type: ignore[arg-type]

    assert len(results) == 2
    assert results[0].paper.id == candidate_a.id
    assert results[0].components["content"] > results[1].components["content"]
    assert results[0].components["collaborative"] == 1.0
    assert any(item.components["graph"] > 0 for item in results)
    assert all(item.explanation.startswith("Được đề xuất vì") for item in results)
