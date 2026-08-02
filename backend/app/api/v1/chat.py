from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import (
    ChatMessage,
    ChatSession,
    Plan,
    ProcessingStatus,
    Subscription,
    UploadedDocument,
    User,
)
from app.schemas.chat import ChatRequest, ChatResponse, CreateChatSessionRequest
from app.services.llm_service import LLMProviderError
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", status_code=201)
async def create_session(
    payload: CreateChatSessionRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    document = await db.get(UploadedDocument, payload.document_id)
    if document is None or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.processing_status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Document is not ready: {document.processing_status.value}",
        )
    session = ChatSession(user_id=user.id, document_id=document.id, title=payload.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": session.id, "title": session.title}


@router.get("/sessions")
async def list_sessions(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    sessions = list(
        (
            await db.scalars(
                select(ChatSession)
                .where(ChatSession.user_id == user.id)
                .order_by(ChatSession.updated_at.desc())
            )
        ).all()
    )
    return [
        {
            "id": item.id,
            "title": item.title,
            "document_id": item.document_id,
            "updated_at": item.updated_at,
        }
        for item in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    session = await db.get(ChatSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat session not found")
    messages = list(
        (
            await db.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at)
            )
        ).all()
    )
    return {
        "id": session.id,
        "title": session.title,
        "document_id": session.document_id,
        "messages": [
            {
                "id": item.id,
                "role": item.role,
                "content": item.content,
                "citations": item.citations,
                "created_at": item.created_at,
            }
            for item in messages
        ],
    }


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    payload: ChatRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    session = await db.get(ChatSession, session_id)
    if session is None or session.user_id != user.id or session.document_id is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not subscription or subscription.plan == Plan.FREE:
        since = datetime.now(UTC) - timedelta(days=1)
        message_count = int(
            await db.scalar(
                select(func.count())
                .select_from(ChatMessage)
                .join(ChatSession, ChatSession.id == ChatMessage.session_id)
                .where(
                    ChatSession.user_id == user.id,
                    ChatMessage.role == "user",
                    ChatMessage.created_at >= since,
                )
            )
            or 0
        )
        if message_count >= settings.max_free_chat_messages_per_day:
            raise HTTPException(status_code=429, detail="Daily chat limit reached for free plan")

    db.add(
        ChatMessage(
            session_id=session.id,
            role="user",
            content=payload.question,
            citations=[],
            token_usage=0,
            created_at=datetime.now(UTC),
        )
    )
    try:
        answer = await RAGService().answer(db, session.document_id, payload.question)
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer.answer,
            citations=[citation.model_dump(mode="json") for citation in answer.citations],
            token_usage=0,
            created_at=datetime.now(UTC),
        )
    )
    session.updated_at = datetime.now(UTC)
    await db.commit()
    return answer


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    session = await db.get(ChatSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat session not found")
    await db.delete(session)
    await db.commit()
    return {"message": "Chat session deleted"}
