from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1 import graphs, library, papers
from app.models.entities import Citation, LibraryItem, Paper, User, UserPaperInteraction, UserRole
from app.services.graph_service import GraphService


class Rows:
    def __init__(self, rows: list[Any]) -> None:
        self.rows = rows

    def all(self) -> list[Any]:
        return self.rows


class FakeDb:
    def __init__(
        self,
        *,
        objects: dict[tuple[type, object], Any] | None = None,
        scalar_values: list[Any] | None = None,
        scalar_batches: list[list[Any]] | None = None,
        execute_batches: list[list[Any]] | None = None,
    ) -> None:
        self.objects = objects or {}
        self.scalar_values = scalar_values or []
        self.scalar_batches = scalar_batches or []
        self.execute_batches = execute_batches or []
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.commit_count = 0

    async def get(self, model: type, key: object) -> Any:
        return self.objects.get((model, key))

    async def scalar(self, _statement: Any) -> Any:
        return self.scalar_values.pop(0) if self.scalar_values else None

    async def scalars(self, _statement: Any) -> Rows:
        return Rows(self.scalar_batches.pop(0) if self.scalar_batches else [])

    async def execute(self, _statement: Any) -> Rows:
        return Rows(self.execute_batches.pop(0) if self.execute_batches else [])

    def add(self, item: Any) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid4()
        self.added.append(item)

    async def delete(self, item: Any) -> None:
        self.deleted.append(item)

    async def commit(self) -> None:
        self.commit_count += 1


def make_user() -> User:
    return User(
        id=uuid4(), email="user@example.com", username="user", password_hash="hash",
        role=UserRole.USER, is_active=True,
    )


def make_paper(title: str = "Graph learning", citations: int = 10) -> Paper:
    return Paper(
        id=uuid4(), title=title, abstract="An abstract", cited_by_count=citations,
        publication_year=2025, is_open_access=True, referenced_works_count=0,
        metadata_json={}, created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_paper_detail_and_related_results() -> None:
    paper = make_paper()
    related = make_paper("Graph representation", 20)
    db = FakeDb(objects={(Paper, paper.id): paper}, scalar_batches=[[related]])
    assert await papers.paper_detail(paper.id, db) is paper  # type: ignore[arg-type]
    results = await papers.related_papers(paper.id, db)  # type: ignore[arg-type]
    assert results == [related]

    with pytest.raises(HTTPException) as exc:
        await papers.paper_detail(uuid4(), FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_library_crud_records_implicit_feedback() -> None:
    user = make_user()
    paper = make_paper()
    save_db = FakeDb(objects={(Paper, paper.id): paper}, scalar_values=[None])
    result = await library.save_paper(
        library.SavePaperRequest(
            paper_id=paper.id,
            collection_name="Reading",
            notes="Important",
            tags=["rag", "rag", "nlp"],
        ),
        user,
        save_db,  # type: ignore[arg-type]
    )
    item = next(value for value in save_db.added if isinstance(value, LibraryItem))
    assert result["message"] == "Saved"
    assert item.tags == ["rag", "nlp"]
    assert any(isinstance(value, UserPaperInteraction) for value in save_db.added)

    item.paper = paper
    list_db = FakeDb(scalar_batches=[[item]])
    items = await library.get_library(user, list_db)  # type: ignore[arg-type]
    assert items[0]["collection_name"] == "Reading"

    update_db = FakeDb(scalar_values=[item])
    updated = await library.update_item(
        paper.id,
        library.UpdateLibraryItemRequest(collection_name="Thesis", tags=["ai", "ai"]),
        user,
        update_db,  # type: ignore[arg-type]
    )
    assert updated["message"] == "Library item updated"
    assert item.tags == ["ai"]

    remove_db = FakeDb(scalar_values=[item])
    removed = await library.remove_paper(paper.id, user, remove_db)  # type: ignore[arg-type]
    assert removed["message"] == "Removed"
    assert remove_db.deleted == [item]
    assert any(
        isinstance(value, UserPaperInteraction) and value.interaction_type == "unsave"
        for value in remove_db.added
    )


@pytest.mark.asyncio
async def test_library_handles_missing_and_duplicate_items() -> None:
    user = make_user()
    paper = make_paper()
    with pytest.raises(HTTPException) as exc:
        await library.save_paper(
            library.SavePaperRequest(paper_id=paper.id),
            user,
            FakeDb(),  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 404

    existing = LibraryItem(
        id=uuid4(), user_id=user.id, paper_id=paper.id, collection_name="Saved", tags=[]
    )
    duplicate_db = FakeDb(objects={(Paper, paper.id): paper}, scalar_values=[existing])
    duplicate = await library.save_paper(
        library.SavePaperRequest(paper_id=paper.id),
        user,
        duplicate_db,  # type: ignore[arg-type]
    )
    assert duplicate["message"] == "Already saved"

    with pytest.raises(HTTPException) as exc:
        await library.remove_paper(paper.id, user, FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_graph_service_filters_edges_and_computes_pagerank() -> None:
    first = make_paper("First", 100)
    second = make_paper("Second", 50)
    outside = uuid4()
    db = FakeDb(
        scalar_batches=[[first, second]],
        execute_batches=[[(first.id, second.id), (outside, first.id)]],
    )
    graph = await GraphService().citation_graph(db, limit=2)  # type: ignore[arg-type]
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["truncated"] is True
    assert sum(node["data"]["pagerank"] for node in graph["nodes"]) == pytest.approx(1.0, abs=1e-5)


@pytest.mark.asyncio
async def test_graph_endpoint_delegates_to_service(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"nodes": [], "edges": [], "truncated": False}

    async def citation_graph(_self: Any, _db: Any, limit: int = 80) -> dict[str, Any]:
        assert limit == 25
        return expected

    monkeypatch.setattr(graphs.GraphService, "citation_graph", citation_graph)
    assert await graphs.citation_graph(25, FakeDb()) == expected  # type: ignore[arg-type]
