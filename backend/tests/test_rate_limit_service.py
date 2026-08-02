import pytest

from app.services.rate_limit_service import RateLimitService


@pytest.mark.asyncio
async def test_in_memory_rate_limit_blocks_after_limit() -> None:
    RateLimitService._memory_counts.clear()
    RateLimitService._memory_expiry.clear()
    first = await RateLimitService._allow_in_memory("test-key", 2, 60)
    second = await RateLimitService._allow_in_memory("test-key", 2, 60)
    third = await RateLimitService._allow_in_memory("test-key", 2, 60)
    assert first == (True, 1)
    assert second == (True, 0)
    assert third == (False, 0)
