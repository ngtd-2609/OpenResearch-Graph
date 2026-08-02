from __future__ import annotations

from io import BytesIO
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1 import documents
from app.models.entities import Plan, ProcessingStatus, Subscription, UploadedDocument, User, UserRole


class ScalarRows:
    def __init__(self, rows: list[Any]) -> None:
        self.rows = rows

    def all(self) -> list[Any]:
        return self.rows


class FakeDb:
    def __init__(
        self,
        *,
        objects: dict[tuple[type, object], Any] | None = None,
        scalar_values: list[Any] | None = None,
        scalar_batches: list[list[Any]] | None = None,
    ) -> None:
        self.objects = objects or {}
        self.scalar_values = scalar_values or []
        self.scalar_batches = scalar_batches or []
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.commit_count = 0

    async def get(self, model: type, key: object) -> Any:
        return self.objects.get((model, key))

    async def scalar(self, _statement: Any) -> Any:
        return self.scalar_values.pop(0) if self.scalar_values else None

    async def scalars(self, _statement: Any) -> ScalarRows:
        return ScalarRows(self.scalar_batches.pop(0) if self.scalar_batches else [])

    def add(self, item: Any) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid4()
        self.added.append(item)

    async def commit(self) -> None:
        self.commit_count += 1

    async def refresh(self, item: Any) -> None:
        if isinstance(item, UploadedDocument):
            item.processing_status = item.processing_status or ProcessingStatus.PENDING
            item.created_at = item.created_at or __import__("datetime").datetime.now(__import__("datetime").UTC)

    async def delete(self, item: Any) -> None:
        self.deleted.append(item)


class FakeStorage:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    async def save_upload(self, _file: UploadFile) -> tuple[str, str, int, str]:
        return "stored.pdf", "documents/stored.pdf", 123, "checksum"

    async def delete(self, path: str) -> None:
        self.deleted.append(path)


def make_user() -> User:
    return User(
        id=uuid4(), email="user@example.com", username="user", password_hash="hash",
        role=UserRole.USER, is_active=True,
    )


def pdf(name: str = "paper.pdf", content_type: str = "application/pdf") -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(b"%PDF-1.4\ncontent"), headers={"content-type": content_type})


def make_document(user: User) -> UploadedDocument:
    return UploadedDocument(
        id=uuid4(), user_id=user.id, original_filename="paper.pdf", stored_filename="stored.pdf",
        mime_type="application/pdf", file_size=123, storage_path="documents/stored.pdf",
        checksum="checksum", processing_status=ProcessingStatus.COMPLETED, page_count=3,
        created_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
    )


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf_and_plan_limit() -> None:
    user = make_user()
    with pytest.raises(HTTPException) as exc:
        await documents.upload_document(pdf("notes.txt", "text/plain"), user, FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 415

    db = FakeDb(
        scalar_values=[Subscription(user_id=user.id, plan=Plan.FREE, status="active"), 3]
    )
    with pytest.raises(HTTPException) as exc:
        await documents.upload_document(pdf(), user, db)  # type: ignore[arg-type]
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_upload_returns_existing_duplicate_and_removes_new_blob(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = make_user()
    duplicate = make_document(user)
    storage = FakeStorage()
    db = FakeDb(scalar_values=[None, 0, duplicate])
    monkeypatch.setattr(documents, "get_storage", lambda: storage)
    response = await documents.upload_document(pdf(), user, db)  # type: ignore[arg-type]
    assert response.id == duplicate.id
    assert storage.deleted == ["documents/stored.pdf"]


@pytest.mark.asyncio
async def test_upload_creates_document_and_queues_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    storage = FakeStorage()
    db = FakeDb(scalar_values=[None, 0, None])
    queued: list[str] = []
    monkeypatch.setattr(documents, "get_storage", lambda: storage)
    monkeypatch.setattr(documents.process_document, "delay", lambda document_id: queued.append(document_id))
    response = await documents.upload_document(pdf(), user, db)  # type: ignore[arg-type]
    assert response.filename == "paper.pdf"
    assert queued == [str(response.id)]
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_document_list_get_and_delete(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    document = make_document(user)
    list_db = FakeDb(scalar_batches=[[document]])
    listed = await documents.list_documents(user, list_db)  # type: ignore[arg-type]
    assert listed[0].pages == 3

    get_db = FakeDb(objects={(UploadedDocument, document.id): document})
    detail = await documents.get_document(document.id, user, get_db)  # type: ignore[arg-type]
    assert detail.filename == "paper.pdf"

    storage = FakeStorage()
    monkeypatch.setattr(documents, "get_storage", lambda: storage)
    delete_db = FakeDb(objects={(UploadedDocument, document.id): document})
    result = await documents.delete_document(document.id, user, delete_db)  # type: ignore[arg-type]
    assert result == {"message": "Document deleted"}
    assert storage.deleted == [document.storage_path]
    assert delete_db.deleted == [document]


@pytest.mark.asyncio
async def test_document_access_is_owner_scoped() -> None:
    user = make_user()
    other = make_user()
    document = make_document(other)
    db = FakeDb(objects={(UploadedDocument, document.id): document})
    with pytest.raises(HTTPException) as exc:
        await documents.get_document(document.id, user, db)  # type: ignore[arg-type]
    assert exc.value.status_code == 404
