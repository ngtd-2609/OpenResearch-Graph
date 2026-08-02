from uuid import UUID

from pydantic import BaseModel, Field


class CreateChatSessionRequest(BaseModel):
    document_id: UUID
    title: str = "PDF chat"


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)


class CitationItem(BaseModel):
    document_id: UUID
    page: int
    chunk_id: UUID
    quote: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    model: str
    latency_ms: int
