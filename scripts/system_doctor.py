from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Check:
    status: str
    name: str
    detail: str
    action: str = ""


def command_version(command: str, *args: str) -> Check:
    executable = shutil.which(command)
    if not executable:
        return Check("ERROR", command, "not found", f"Install {command} and open a new PowerShell window.")
    result = subprocess.run([executable, *args], capture_output=True, text=True, timeout=15, check=False)
    detail = (result.stdout or result.stderr).strip().splitlines()
    return Check("OK" if result.returncode == 0 else "ERROR", command, detail[0] if detail else executable)


def tcp_check(name: str, host: str, port: int, *, required: bool) -> Check:
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return Check("OK", name, f"{host}:{port}")
    except OSError:
        status = "ERROR" if required else "WARNING"
        return Check(status, name, f"cannot connect to {host}:{port}", f"Run: docker compose up -d {name.lower()}")


def http_check(name: str, url: str) -> Check:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            body = response.read(500).decode("utf-8", errors="replace")
            return Check("OK", name, f"HTTP {response.status} {body[:100]}")
    except (urllib.error.URLError, TimeoutError) as exc:
        return Check("WARNING", name, str(exc), "Check docker compose ps and service logs.")


def env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    checks = [
        command_version("git", "--version"),
        command_version("python", "--version"),
        command_version("node", "--version"),
        command_version("npm", "--version"),
        command_version("docker", "--version"),
    ]
    if shutil.which("docker"):
        checks.append(command_version("docker", "compose", "version"))

    env_path = Path(".env")
    values = env_values(env_path)
    checks.append(
        Check("OK", ".env", "loaded")
        if values
        else Check("WARNING", ".env", "missing or empty", "Copy-Item .env.example .env")
    )
    checks.extend(
        [
            tcp_check("PostgreSQL", "localhost", 5432, required=True),
            tcp_check("Redis", "localhost", 6379, required=True),
            http_check("Backend", "http://localhost:8000/health"),
            http_check("Frontend", "http://localhost:3000"),
        ]
    )

    mode_checks = [
        ("OpenAlex", values.get("OPENALEX_MODE", "seed"), "seed"),
        ("LLM", values.get("LLM_PROVIDER", "mock"), "mock"),
        ("Stripe", values.get("BILLING_MODE", "mock"), "mock"),
        ("Email", values.get("EMAIL_BACKEND", "console"), "console"),
        ("Storage", values.get("STORAGE_BACKEND", "local"), "local"),
    ]
    for name, mode, fallback in mode_checks:
        status = "WARNING" if mode == fallback else "OK"
        checks.append(Check(status, name, f"mode={mode}", f"{fallback} is valid for development." if status == "WARNING" else ""))

    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")
        if check.action:
            print(f"       Action: {check.action}")

    summary = {status: sum(item.status == status for item in checks) for status in ("OK", "WARNING", "ERROR")}
    print("\nSummary:", json.dumps(summary))
    return 1 if summary["ERROR"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
