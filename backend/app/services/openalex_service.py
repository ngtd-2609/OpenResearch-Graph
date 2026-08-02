import asyncio
from collections.abc import AsyncIterator
from datetime import date
from typing import Any

import httpx

from app.core.config import settings

WORK_SELECT_FIELDS = (
    "id,doi,display_name,abstract_inverted_index,publication_date,publication_year,"
    "language,cited_by_count,referenced_works,open_access,primary_location,type,"
    "authorships,topics"
)


class OpenAlexService:
    """Resilient async client for search and cursor-based OpenAlex ingestion."""

    def __init__(self) -> None:
        self.base_url = settings.openalex_base_url.rstrip("/")

    @property
    def configured(self) -> bool:
        """True when mode=api and at least one credential is set (key or polite email)."""
        return settings.openalex_mode == "api" and bool(
            settings.openalex_api_key or settings.openalex_email
        )

    async def search_works(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        return await self._request_works(
            {
                "search": query,
                "page": page,
                "per_page": min(per_page, 100),
                "select": WORK_SELECT_FIELDS,
            }
        )

    async def work_page(
        self,
        *,
        query: str,
        cursor: str,
        per_page: int = 100,
    ) -> dict[str, Any]:
        return await self._request_works(
            {
                "search": query,
                "cursor": cursor,
                "per_page": min(per_page, 100),
                "select": WORK_SELECT_FIELDS,
            }
        )

    async def _request_works(self, params: dict[str, Any]) -> dict[str, Any]:
        if not self.configured:
            return {"meta": {"count": 0, "next_cursor": None}, "results": []}
        # Prefer API key (authenticated); fall back to polite pool (mailto)
        if settings.openalex_api_key:
            request_params = {**params, "api_key": settings.openalex_api_key}
        else:
            request_params = {**params, "mailto": settings.openalex_email}
        timeout = httpx.Timeout(30.0, connect=10.0)
        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(5):
                try:
                    response = await client.get(f"{self.base_url}/works", params=request_params)
                    if response.status_code == 429:
                        retry_after = min(float(response.headers.get("Retry-After", "2")), 60.0)
                        await asyncio.sleep(retry_after)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    if not isinstance(data, dict) or not isinstance(data.get("results", []), list):
                        raise ValueError("Unexpected OpenAlex response schema")
                    return data
                except (httpx.HTTPError, ValueError) as exc:
                    last_error = exc
                    if attempt < 4:
                        await asyncio.sleep(min(2**attempt, 16))
        raise RuntimeError(f"OpenAlex request failed: {last_error}") from last_error

    async def iter_work_pages(
        self,
        query: str,
        *,
        max_records: int,
        start_cursor: str = "*",
        per_page: int = 100,
    ) -> AsyncIterator[tuple[list[dict[str, Any]], str | None]]:
        cursor: str | None = start_cursor
        emitted = 0
        while cursor and emitted < max_records:
            data = await self.work_page(
                query=query,
                cursor=cursor,
                per_page=min(per_page, max_records - emitted),
            )
            results = list(data.get("results") or [])
            if not results:
                return
            emitted += len(results)
            next_cursor = (data.get("meta") or {}).get("next_cursor")
            yield results, next_cursor
            cursor = next_cursor

    async def iter_works(
        self,
        query: str,
        max_records: int,
        per_page: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        async for results, _ in self.iter_work_pages(
            query,
            max_records=max_records,
            per_page=per_page,
        ):
            for item in results:
                yield item

    @staticmethod
    def normalize_work(item: dict[str, Any]) -> dict[str, Any]:
        open_access = item.get("open_access") or {}
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        publication_date = None
        if item.get("publication_date"):
            try:
                publication_date = date.fromisoformat(item["publication_date"])
            except (TypeError, ValueError):
                publication_date = None
        return {
            "openalex_id": item.get("id"),
            "doi": item.get("doi"),
            "title": item.get("display_name") or item.get("title") or "Untitled",
            "abstract": reconstruct_abstract(item.get("abstract_inverted_index")),
            "publication_date": publication_date,
            "publication_year": item.get("publication_year"),
            "language": item.get("language"),
            "cited_by_count": max(0, int(item.get("cited_by_count") or 0)),
            "referenced_works_count": len(item.get("referenced_works") or []),
            "is_open_access": bool(open_access.get("is_oa", False)),
            "open_access_url": open_access.get("oa_url"),
            "pdf_url": primary_location.get("pdf_url") or open_access.get("oa_url"),
            "source_name": source.get("display_name"),
            "type": item.get("type"),
            "metadata_json": item,
        }


def reconstruct_abstract(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    pairs = [
        (position, word)
        for word, positions in index.items()
        for position in positions
        if isinstance(position, int)
    ]
    return " ".join(word for _, word in sorted(pairs)) or None
