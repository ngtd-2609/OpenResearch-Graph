from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Awaitable, Callable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - dependency exists in deployed environments.
    Redis = None  # type: ignore[assignment]


class IntegrationService:
    """Build safe integration health summaries without exposing credentials."""

    async def _check(
        self,
        name: str,
        configured: bool,
        check: Callable[[], Awaitable[None]] | None,
        *,
        fallback_status: str,
    ) -> dict[str, Any]:
        started = perf_counter()
        status = fallback_status
        message = "Configuration is present" if configured else "Using development fallback"
        if check is not None:
            try:
                await check()
                status = "healthy"
                message = "Connection succeeded"
            except Exception as exc:  # Health endpoint must report failures rather than crash.
                status = "error"
                message = f"{type(exc).__name__}: {str(exc)[:160]}"
        return {
            "name": name,
            "configured": configured,
            "status": status,
            "message": message,
            "latency_ms": round((perf_counter() - started) * 1000, 2),
            "checked_at": datetime.now(UTC).isoformat(),
        }

    async def statuses(self, db: AsyncSession) -> list[dict[str, Any]]:
        async def database_check() -> None:
            await db.execute(text("SELECT 1"))

        async def redis_check() -> None:
            if Redis is None:
                raise RuntimeError("redis package is not installed")
            client = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
            try:
                await client.ping()
            finally:
                await client.aclose()

        async def storage_check() -> None:
            if settings.storage_backend != "local":
                return
            path = Path(settings.local_storage_path)
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".integration-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)

        return [
            await self._check("postgresql", True, database_check, fallback_status="unknown"),
            await self._check("redis", True, redis_check, fallback_status="unknown"),
            await self._check(
                "openalex",
                bool(settings.openalex_api_key) and settings.openalex_mode == "api",
                None,
                fallback_status="configured" if settings.openalex_mode == "api" else "seed-mode",
            ),
            await self._check(
                "llm",
                settings.llm_provider != "mock",
                None,
                fallback_status=settings.llm_provider,
            ),
            await self._check(
                "stripe",
                settings.billing_mode == "stripe",
                None,
                fallback_status=settings.billing_mode,
            ),
            await self._check(
                "email",
                settings.email_backend != "console",
                None,
                fallback_status=settings.email_backend,
            ),
            await self._check(
                "storage",
                True,
                storage_check,
                fallback_status=settings.storage_backend,
            ),
        ]
