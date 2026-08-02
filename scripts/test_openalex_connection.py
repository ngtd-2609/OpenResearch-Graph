from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.openalex_service import OpenAlexService  # noqa: E402


def masked(value: str) -> str:
    return f"{value[:4]}...{value[-4:]}" if len(value) >= 10 else "configured"


async def main() -> int:
    service = OpenAlexService()
    key = os.getenv("OPENALEX_API_KEY", "")
    print(f"OpenAlex mode: {os.getenv('OPENALEX_MODE', 'seed')}")
    print(f"API key: {masked(key) if key else 'NOT CONFIGURED'}")
    if not service.configured:
        print("Connection status: SKIPPED (seed mode)")
        return 0
    started = perf_counter()
    try:
        data = await service.search_works("machine learning", per_page=1)
        paper = (data.get("results") or [None])[0]
        print("Connection status: OK")
        print(f"Sample paper fetched: {'YES' if paper else 'NO'}")
        print(f"Latency: {round((perf_counter() - started) * 1000)} ms")
        return 0 if paper else 1
    except Exception as exc:
        print(f"Connection status: ERROR ({type(exc).__name__}: {exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
