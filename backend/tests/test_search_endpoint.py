from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

from app.api.v1 import search
from app.models.entities import Paper, User, UserRole


def request() -> Request:
    return Request(
        {
            "type": "http", "method": "GET", "path": "/search/papers",
            "headers": [], "query_string": b"", "client": ("127.0.0.1", 1234),
            "server": ("test", 80), "scheme": "http",
        }
    )


def paper() -> Paper:
    return Paper(
        id=uuid4(), title="Neural retrieval", abstract="Abstract", publication_year=2025,
        cited_by_count=10, is_open_access=True, referenced_works_count=0, metadata_json={},
    )


async def call(**overrides: Any):
    values = {
        "request": request(), "response": Response(), "query": "neural retrieval",
        "page": 1, "per_page": 20, "from_year": None, "to_year": None,
        "open_access": None, "author": None, "institution": None, "topic": None,
        "paper_type": None, "user": None, "db": object(),
    }
    values.update(overrides)
    return await search.search_papers(**values)


@pytest.mark.asyncio
async def test_search_rejects_invalid_date_range() -> None:
    with pytest.raises(HTTPException) as exc:
        await call(from_year=2025, to_year=2020)
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_search_enforces_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    async def deny(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return False, 0

    monkeypatch.setattr(search.RateLimitService, "allow", deny)
    with pytest.raises(HTTPException) as exc:
        await call()
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_search_returns_local_hybrid_results(monkeypatch: pytest.MonkeyPatch) -> None:
    item = paper()

    async def allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 19

    async def local(*_args: Any, **_kwargs: Any) -> tuple[int, list[Paper]]:
        return 1, [item]

    monkeypatch.setattr(search.RateLimitService, "allow", allow)
    monkeypatch.setattr(search.PaperSearchService, "search", local)
    response = Response()
    result = await call(response=response)
    assert result.total == 1
    assert result.items[0].id == item.id
    assert response.headers["X-RateLimit-Remaining"] == "19"


@pytest.mark.asyncio
async def test_search_uses_premium_limit_for_privileged_user(monkeypatch: pytest.MonkeyPatch) -> None:
    user = User(
        id=uuid4(), email="premium@example.com", username="premium", password_hash="hash",
        role=UserRole.PREMIUM, is_active=True,
    )
    captured: dict[str, int] = {}

    async def allow(_self: Any, _key: str, limit: int) -> tuple[bool, int]:
        captured["limit"] = limit
        return True, limit - 1

    async def local(*_args: Any, **_kwargs: Any) -> tuple[int, list[Paper]]:
        return 0, []

    monkeypatch.setattr(search.RateLimitService, "allow", allow)
    monkeypatch.setattr(search.PaperSearchService, "search", local)
    monkeypatch.setattr(search.OpenAlexService, "configured", property(lambda _self: False))
    await call(user=user)
    assert captured["limit"] == search.settings.premium_searches_per_hour


@pytest.mark.asyncio
async def test_search_falls_back_to_normalized_openalex_data(monkeypatch: pytest.MonkeyPatch) -> None:
    async def allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 10

    async def local(*_args: Any, **_kwargs: Any) -> tuple[int, list[Paper]]:
        return 0, []

    async def remote(_self: Any, _query: str, _page: int, _per_page: int, **_kwargs: Any) -> dict[str, Any]:
        return {
            "meta": {"count": 12},
            "results": [{"id": "https://openalex.org/W1", "display_name": "Remote paper"}],
        }

    def normalize(_item: dict[str, Any]) -> dict[str, Any]:
        return {
            "openalex_id": "W1", "title": "Remote paper", "abstract": None,
            "publication_year": 2024, "cited_by_count": 2, "is_open_access": False,
            "referenced_works_count": 0, "metadata_json": {},
        }

    monkeypatch.setattr(search.RateLimitService, "allow", allow)
    monkeypatch.setattr(search.PaperSearchService, "search", local)
    monkeypatch.setattr(search.OpenAlexService, "configured", property(lambda _self: True))
    monkeypatch.setattr(search.OpenAlexService, "search_works", remote)
    monkeypatch.setattr(search.OpenAlexService, "normalize_work", staticmethod(normalize))
    result = await call()
    assert result.total == 12
    assert result.items[0].title == "Remote paper"
