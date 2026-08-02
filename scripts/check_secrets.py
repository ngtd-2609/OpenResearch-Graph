"""Fail on high-confidence secrets or accidentally tracked local environment files.

This lightweight repository guard is intentionally conservative. Production CI should
also use a dedicated scanner such as Gitleaks or TruffleHog.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("OpenAI-style API key", re.compile(r"\bsk-(?:live|test)?-?[A-Za-z0-9_-]{32,}\b")),
    ("Stripe live/test secret", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("Stripe webhook secret", re.compile(r"\bwhsec_[A-Za-z0-9]{20,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
)
SKIP_PARTS = {".git", "node_modules", ".next", "__pycache__", ".venv", ".pytest_cache"}
SKIP_FILES = {"check_secrets.py"}


def tracked_files() -> set[str]:
    if not (ROOT / ".git").exists():
        return set()
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    return set(result.stdout.splitlines())


def main() -> int:
    tracked = tracked_files()
    errors: list[str] = []
    for forbidden in {".env", "backend/.env", "frontend/.env.local"}:
        if forbidden in tracked:
            errors.append(f"{forbidden} is tracked by Git")

    for path in ROOT.rglob("*"):
        try:
            relative = path.relative_to(ROOT)
            if (
                not path.is_file()
                or path.is_symlink()
                or path.name in SKIP_FILES
                or any(part in SKIP_PARTS for part in relative.parts)
            ):
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in PATTERNS:
            if pattern.search(text):
                errors.append(f"possible {label} in {relative}")

    if errors:
        print("\n".join(f"[ERROR] {item}" for item in sorted(set(errors))))
        return 1
    print("[OK] No high-confidence secrets found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
