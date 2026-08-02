from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1 import chat
from app.models.entities import (
    ChatMessage,
    ChatSession,
    Plan,
    ProcessingStatus,
    Subscription,
    UploadedDocument,
    User,
    UserRole,
)
from app.schemas.chat import ChatRequest, ChatResponse, CitationItem, CreateChatSessionRequest
from app.services.llm_service import LLMProviderError


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

    async def refresh(self, _item: Any) -> None:
        return None

    async def delete(self, item: Any) -> None:
        self.deleted.append(item)


def make_user() -> User:
    return User(
        id=uuid4(), email="user@example.com", username="user", password_hash="hash",
        role=UserRole.USER, is_active=True,
    )


def make_document(user: User, status: ProcessingStatus = ProcessingStatus.COMPLETED) -> UploadedDocument:
    return UploadedDocument(
        id=uuid4(), user_id=user.id, original_filename="paper.pdf", stored_filename="paper.pdf",
        mime_type="application/pdf", file_size=100, storage_path="paper.pdf", checksum="abc",
        processing_status=status, page_count=2,
    )


@pytest.mark.asyncio
async def test_create_session_checks_document_ownership_and_status() -> None:
    user = make_user()
    missing_id = uuid4()
    with pytest.raises(HTTPException) as exc:
        await chat.create_session(
            CreateChatSessionRequest(document_id=missing_id, title="Chat"),
            user,
            FakeDb(),  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 404

    document = make_document(user, ProcessingStatus.RUNNING)
    db = FakeDb(objects={(UploadedDocument, document.id): document})
    with pytest.raises(HTTPException) as exc:
        await chat.create_session(
            CreateChatSessionRequest(document_id=document.id, title="Chat"),
            user,
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_list_get_and_delete_chat_session() -> None:
    user = make_user()
    document = make_document(user)
    db = FakeDb(objects={(UploadedDocument, document.id): document})
    created = await chat.create_session(
        CreateChatSessionRequest(document_id=document.id, title="Research chat"),
        user,
        db,  # type: ignore[arg-type]
    )
    session = next(item for item in db.added if isinstance(item, ChatSession))
    session.updated_at = datetime.now(UTC)
    assert created["title"] == "Research chat"

    list_db = FakeDb(scalar_batches=[[session]])
    listed = await chat.list_sessions(user, list_db)  # type: ignore[arg-type]
    assert listed[0]["document_id"] == document.id

    message = ChatMessage(
        id=uuid4(), session_id=session.id, role="assistant", content="Answer",
        citations=[], token_usage=0, created_at=datetime.now(UTC),
    )
    detail_db = FakeDb(
        objects={(ChatSession, session.id): session},
        scalar_batches=[[message]],
    )
    detail = await chat.get_session(session.id, user, detail_db)  # type: ignore[arg-type]
    assert detail["messages"][0]["content"] == "Answer"

    delete_db = FakeDb(objects={(ChatSession, session.id): session})
    result = await chat.delete_session(session.id, user, delete_db)  # type: ignore[arg-type]
    assert result == {"message": "Chat session deleted"}
    assert delete_db.deleted == [session]


@pytest.mark.asyncio
async def test_send_message_enforces_free_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    session = ChatSession(id=uuid4(), user_id=user.id, document_id=uuid4(), title="Chat")
    subscription = Subscription(user_id=user.id, plan=Plan.FREE, status="active")
    db = FakeDb(
        objects={(ChatSession, session.id): session},
        scalar_values=[subscription, 20],
    )
    monkeypatch.setattr(chat.settings, "max_free_chat_messages_per_day", 20)
    with pytest.raises(HTTPException) as exc:
        await chat.send_message(
            session.id,
            ChatRequest(question="Explain the method"),
            user,
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_send_message_persists_grounded_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    session = ChatSession(id=uuid4(), user_id=user.id, document_id=uuid4(), title="Chat")
    subscription = Subscription(user_id=user.id, plan=Plan.PREMIUM, status="active")
    db = FakeDb(objects={(ChatSession, session.id): session}, scalar_values=[subscription])
    response = ChatResponse(
        answer="The method minimizes the objective.",
        citations=[CitationItem(document_id=session.document_id, page=2, chunk_id=uuid4(), quote="objective", score=0.91)],
        model="mock", latency_ms=5,
    )

    async def answer(_self: Any, _db: Any, _document_id: Any, _question: str) -> ChatResponse:
        return response

    monkeypatch.setattr(chat.RAGService, "answer", answer)
    actual = await chat.send_message(
        session.id,
        ChatRequest(question="What does it do?"),
        user,
        db,  # type: ignore[arg-type]
    )
    assert actual.answer == response.answer
    assert [item.role for item in db.added] == ["user", "assistant"]
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_send_message_translates_llm_failure_to_bad_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    session = ChatSession(id=uuid4(), user_id=user.id, document_id=uuid4(), title="Chat")
    subscription = Subscription(user_id=user.id, plan=Plan.PREMIUM, status="active")
    db = FakeDb(objects={(ChatSession, session.id): session}, scalar_values=[subscription])

    async def fail(*_args: Any, **_kwargs: Any) -> ChatResponse:
        raise LLMProviderError("Provider unavailable")

    monkeypatch.setattr(chat.RAGService, "answer", fail)
    with pytest.raises(HTTPException) as exc:
        await chat.send_message(
            session.id,
            ChatRequest(question="Question"),
            user,
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 502
