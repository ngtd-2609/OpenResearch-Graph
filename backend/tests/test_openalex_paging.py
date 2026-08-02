import pytest

from app.services.openalex_service import OpenAlexService


@pytest.mark.asyncio
async def test_iter_work_pages_stops_at_requested_record_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    service = OpenAlexService()
    calls: list[str] = []

    async def fake_work_page(query: str, *, cursor: str, per_page: int):
        calls.append(cursor)
        if cursor == "*":
            return {
                "results": [{"id": "W1"}, {"id": "W2"}][:per_page],
                "meta": {"next_cursor": "cursor-2"},
            }
        return {
            "results": [{"id": "W3"}, {"id": "W4"}][:per_page],
            "meta": {"next_cursor": None},
        }

    monkeypatch.setattr(service, "work_page", fake_work_page)
    pages = []
    async for items, cursor in service.iter_work_pages("graph", max_records=3, per_page=2):
        pages.append((items, cursor))

    assert calls == ["*", "cursor-2"]
    assert [item["id"] for page, _ in pages for item in page] == ["W1", "W2", "W3"]
