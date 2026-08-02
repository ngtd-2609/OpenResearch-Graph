from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import settings  # noqa: E402
from app.services.llm_service import Message, get_llm  # noqa: E402


async def main() -> int:
    print(f"Provider: {settings.llm_provider}")
    print(f"Model: {settings.llm_model or settings.ollama_model or 'mock'}")
    started = perf_counter()
    try:
        response = await get_llm().generate(
            [Message(role="user", content="Reply with exactly: connection ok")]
        )
        print("Connection status: OK" if response.text else "Connection status: ERROR")
        print(f"Generation status: {'OK' if response.text else 'EMPTY'}")
        print(f"Latency: {round((perf_counter() - started) * 1000)} ms")
        return 0 if response.text else 1
    except Exception as exc:
        print(f"Connection status: ERROR ({type(exc).__name__}: {exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
