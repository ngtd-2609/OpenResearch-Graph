import asyncio
import logging
import time
from collections import defaultdict

try:
    from redis.asyncio import Redis
except ImportError:
    Redis = None  # type: ignore[assignment]

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitService:
    """Fixed-window limiter backed by Redis with a bounded in-process fallback."""

    _memory_counts: dict[str, int] = defaultdict(int)
    _memory_expiry: dict[str, float] = {}
    _lock = asyncio.Lock()

    async def allow(
        self,
        identity: str,
        limit: int,
        window_seconds: int = 3_600,
    ) -> tuple[bool, int]:
        window = int(time.time() // window_seconds)
        key = f"rate:{identity}:{window}"
        if Redis is not None:
            try:
                redis = Redis.from_url(settings.redis_url, decode_responses=True)
                async with redis.pipeline(transaction=True) as pipeline:
                    pipeline.incr(key)
                    pipeline.expire(key, window_seconds, nx=True)
                    count, _ = await pipeline.execute()
                await redis.aclose()
                numeric_count = int(count)
                return numeric_count <= limit, max(0, limit - numeric_count)
            except Exception as exc:
                logger.warning(
                    "Redis rate limiter unavailable; using bounded memory fallback: %s",
                    type(exc).__name__,
                )
        return await self._allow_in_memory(key, limit, window_seconds)

    @classmethod
    async def _allow_in_memory(
        cls,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        now = time.time()
        async with cls._lock:
            expired = [item for item, expiry in cls._memory_expiry.items() if expiry <= now]
            for item in expired:
                cls._memory_expiry.pop(item, None)
                cls._memory_counts.pop(item, None)
            cls._memory_counts[key] += 1
            cls._memory_expiry.setdefault(key, now + window_seconds)
            count = cls._memory_counts[key]
        return count <= limit, max(0, limit - count)
