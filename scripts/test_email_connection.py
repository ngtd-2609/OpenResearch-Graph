from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import settings  # noqa: E402
from app.services.email_service import EmailService  # noqa: E402


async def main() -> int:
    try:
        await EmailService().send_action_link(
            "developer@example.com",
            "OpenResearch email probe",
            "http://localhost:3000/email-probe",
        )
        print(f"Email backend: {settings.email_backend}")
        print("Send status: OK")
        print("Console mode: inspect backend logs; Mailpit: open http://localhost:8025")
        return 0
    except Exception as exc:
        print(f"Send status: ERROR ({type(exc).__name__}: {exc})")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
