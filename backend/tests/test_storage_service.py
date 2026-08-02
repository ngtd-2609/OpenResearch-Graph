from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.services.storage_service import LocalStorage


@pytest.mark.asyncio
async def test_local_storage_streams_hashes_materializes_and_deletes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("app.services.storage_service.settings.local_storage_path", str(tmp_path))
    monkeypatch.setattr("app.services.storage_service.settings.max_upload_size_mb", 1)
    storage = LocalStorage()
    upload = UploadFile(filename="paper.pdf", file=BytesIO(b"pdf-content"))

    stored_name, path, size, checksum = await storage.save_upload(upload)
    assert stored_name.endswith(".pdf")
    assert size == len(b"pdf-content")
    assert len(checksum) == 64
    assert Path(await storage.materialize(path)).read_bytes() == b"pdf-content"

    await storage.delete(path)
    assert not Path(path).exists()


@pytest.mark.asyncio
async def test_local_storage_blocks_path_escape(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("app.services.storage_service.settings.local_storage_path", str(tmp_path))
    storage = LocalStorage()
    with pytest.raises(ValueError, match="escapes"):
        await storage.delete(str(tmp_path.parent / "unmanaged.pdf"))


@pytest.mark.asyncio
async def test_local_storage_removes_partial_file_when_upload_exceeds_limit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("app.services.storage_service.settings.local_storage_path", str(tmp_path))
    monkeypatch.setattr("app.services.storage_service.settings.max_upload_size_mb", 0)
    storage = LocalStorage()
    upload = UploadFile(filename="paper.pdf", file=BytesIO(b"too-large"))
    with pytest.raises(ValueError, match="upload limit"):
        await storage.save_upload(upload)
    assert list(tmp_path.iterdir()) == []
