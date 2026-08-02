from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserPublic(ORMModel):
    id: UUID
    email: str
    username: str
    full_name: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class PaperPublic(ORMModel):
    id: UUID
    openalex_id: str | None
    doi: str | None
    title: str
    abstract: str | None
    publication_year: int | None
    cited_by_count: int
    is_open_access: bool
    open_access_url: str | None
    source_name: str | None


class PaginatedPapers(BaseModel):
    query: str
    total: int
    page: int
    per_page: int
    items: list[PaperPublic]
