from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Protocol
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class StorageProvider(Protocol):
    async def save_upload(self, file: UploadFile) -> tuple[str, str, int, str]: ...
    async def delete(self, path: str) -> None: ...
    async def materialize(self, path: str) -> str: ...


def _safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "document.pdf").suffix.lower()
    return suffix if suffix in {".pdf"} else ".pdf"


class LocalStorage:
    """Private local storage restricted to the configured root directory."""

    def __init__(self) -> None:
        self.root = Path(settings.local_storage_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_managed_path(self, path: str) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError("Storage path escapes configured root")
        return resolved

    async def save_upload(self, file: UploadFile) -> tuple[str, str, int, str]:
        stored_name = f"{uuid4().hex}{_safe_suffix(file.filename)}"
        destination = self._resolve_managed_path(stored_name)
        digest = hashlib.sha256()
        size = 0
        try:
            with destination.open("xb") as output:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > settings.upload_limit_bytes:
                        raise ValueError("File exceeds configured upload limit")
                    digest.update(chunk)
                    output.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return stored_name, str(destination), size, digest.hexdigest()

    async def delete(self, path: str) -> None:
        self._resolve_managed_path(path).unlink(missing_ok=True)

    async def materialize(self, path: str) -> str:
        resolved = self._resolve_managed_path(path)
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        return str(resolved)


class S3Storage:
    """S3-compatible private-object adapter."""

    def __init__(self) -> None:
        if not settings.s3_bucket:
            raise ValueError("S3_BUCKET is required for s3-compatible storage")
        import boto3

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )
        self.bucket = settings.s3_bucket

    def _key(self, path: str) -> str:
        prefix = f"s3://{self.bucket}/"
        if path.startswith("s3://") and not path.startswith(prefix):
            raise ValueError("Object belongs to another bucket")
        key = path[len(prefix) :] if path.startswith(prefix) else path
        key = key.strip("/")
        if not key or ".." in Path(key).parts:
            raise ValueError("Invalid object key")
        return key

    async def save_upload(self, file: UploadFile) -> tuple[str, str, int, str]:
        stored_name = f"{uuid4().hex}{_safe_suffix(file.filename)}"
        digest = hashlib.sha256()
        size = 0
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            try:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > settings.upload_limit_bytes:
                        raise ValueError("File exceeds configured upload limit")
                    digest.update(chunk)
                    temporary.write(chunk)
                temporary.flush()
                await asyncio.to_thread(
                    self.client.upload_file,
                    str(temporary_path),
                    self.bucket,
                    stored_name,
                    ExtraArgs={"ContentType": file.content_type or "application/pdf"},
                )
            finally:
                temporary_path.unlink(missing_ok=True)
        return stored_name, f"s3://{self.bucket}/{stored_name}", size, digest.hexdigest()

    async def delete(self, path: str) -> None:
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket,
            Key=self._key(path),
        )

    async def materialize(self, path: str) -> str:
        key = self._key(path)
        temporary = NamedTemporaryFile(suffix=".pdf", delete=False)
        temporary.close()
        await asyncio.to_thread(self.client.download_file, self.bucket, key, temporary.name)
        return temporary.name


def get_storage() -> StorageProvider:
    return S3Storage() if settings.storage_backend == "s3-compatible" else LocalStorage()
