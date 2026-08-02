from pathlib import Path
from typing import Any

import pytest

from app.services.integration_service import IntegrationService


class FakeDb:
    async def execute(self, _statement: Any) -> None:
        return None


@pytest.mark.asyncio
async def test_statuses_report_fallbacks_without_leaking_secrets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("app.services.integration_service.Redis", None)
    monkeypatch.setattr("app.services.integration_service.settings.local_storage_path", str(tmp_path))
    monkeypatch.setattr("app.services.integration_service.settings.openalex_mode", "seed")
    monkeypatch.setattr("app.services.integration_service.settings.openalex_api_key", "")
    monkeypatch.setattr("app.services.integration_service.settings.llm_provider", "mock")

    rows = await IntegrationService().statuses(FakeDb())  # type: ignore[arg-type]
    by_name = {row["name"]: row for row in rows}

    assert by_name["postgresql"]["status"] == "healthy"
    assert by_name["redis"]["status"] == "error"
    assert by_name["openalex"]["status"] == "seed-mode"
    assert by_name["storage"]["status"] == "healthy"
    assert all("secret" not in str(row).lower() for row in rows)
