from __future__ import annotations

import asyncio
import sys
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import settings  # noqa: E402
from app.services.storage_service import get_storage  # noqa: E402


async def main() -> int:
    storage = get_storage()
    upload = UploadFile(filename="storage-probe.pdf", file=BytesIO(b"%PDF-1.4\nprobe"))
    path = ""
    try:
        _, path, size, checksum = await storage.save_upload(upload)
        materialized = await storage.materialize(path)
        print(f"Storage backend: {settings.storage_backend}")
        print(f"Write: OK ({size} bytes, sha256={checksum[:12]}...)")
        print(f"Materialize: OK ({materialized})")
        return 0
    except Exception as exc:
        print(f"Storage test: ERROR ({type(exc).__name__}: {exc})")
        return 1
    finally:
        if path:
            await storage.delete(path)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
