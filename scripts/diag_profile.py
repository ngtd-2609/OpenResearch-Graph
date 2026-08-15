"""Measure microsecond timings of security and recommendation components."""
import asyncio
import time
from app.core.security import hash_password, verify_password
from app.db.session import AsyncSessionLocal
from app.services.recommendation_service import RecommendationService
from app.services.rate_limit_service import RateLimitService
from app.models.entities import User
from sqlalchemy import select


async def test():
    # 1. RateLimitService timing
    t0 = time.perf_counter()
    allowed, remaining = await RateLimitService().allow("test-identity", 10)
    t_rate = (time.perf_counter() - t0) * 1000.0
    print(f"RateLimitService.allow: {t_rate:.3f}ms (allowed={allowed}, remaining={remaining})")

    # 2. Password verification timing
    t0 = time.perf_counter()
    pwd_hash = hash_password("Student123!")
    t_hash = (time.perf_counter() - t0) * 1000.0
    print(f"Argon2 hash_password: {t_hash:.3f}ms")

    t0 = time.perf_counter()
    valid = verify_password("Student123!", pwd_hash)
    t_verify = (time.perf_counter() - t0) * 1000.0
    print(f"Argon2 verify_password: {t_verify:.3f}ms (valid={valid})")

    # 3. DB fetch timing
    async with AsyncSessionLocal() as db:
        t0 = time.perf_counter()
        user = await db.scalar(select(User).where(User.email == "user@openresearch.dev"))
        t_db = (time.perf_counter() - t0) * 1000.0
        print(f"DB select User: {t_db:.3f}ms (user={user.username if user else 'none'})")

        # 4. Recommendation timing
        t0 = time.perf_counter()
        recs = await RecommendationService().recommend(db, user.id, limit=10)
        t_rec = (time.perf_counter() - t0) * 1000.0
        print(f"RecommendationService.recommend (limit=10): {t_rec:.3f}ms (items={len(recs)})")


if __name__ == "__main__":
    asyncio.run(test())
