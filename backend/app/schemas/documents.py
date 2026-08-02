from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.entities import ProcessingStatus


class DocumentPublic(BaseModel):
    id: UUID
    filename: str
    status: ProcessingStatus
    pages: int | None = None
    file_size: int
    error: str | None = None
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    status: ProcessingStatus
