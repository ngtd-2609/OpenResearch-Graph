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
    _redis_client: object | None = None
    _redis_disabled_until: float = 0.0

    @classmethod
    def _get_redis(cls) -> object | None:
        if Redis is None or time.time() < cls._redis_disabled_until:
            return None
        if cls._redis_client is None:
            try:
                cls._redis_client = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=0.05,
                    socket_timeout=0.05,
                )
            except Exception:
                cls._redis_disabled_until = time.time() + 60.0
                return None
        return cls._redis_client

    async def allow(
        self,
        identity: str,
        limit: int,
        window_seconds: int = 3_600,
    ) -> tuple[bool, int]:
        window = int(time.time() // window_seconds)
        key = f"rate:{identity}:{window}"
        redis = self._get_redis()
        if redis is not None:
            try:
                async with redis.pipeline(transaction=True) as pipeline:
                    pipeline.incr(key)
                    pipeline.expire(key, window_seconds, nx=True)
                    count, _ = await pipeline.execute()
                numeric_count = int(count)
                return numeric_count <= limit, max(0, limit - numeric_count)
            except Exception as exc:
                RateLimitService._redis_disabled_until = time.time() + 60.0
                logger.debug(
                    "Redis rate limiter failed, failing over to memory for 60s: %s",
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
