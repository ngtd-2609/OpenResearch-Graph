from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from pgvector.sqlalchemy import Vector
except ImportError:  # Allows mock-mode imports before optional DB packages are installed.
    from sqlalchemy.types import TypeDecorator

    class Vector(TypeDecorator):
        impl = JSON
        cache_ok = True

        def __init__(self, dimension: int | None = None) -> None:
            super().__init__()

from app.core.config import settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


def json_column_type() -> JSON:
    return JSON().with_variant(JSONB(), "postgresql")


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]


class UserRole(StrEnum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class Plan(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(160))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=enum_values),
        default=UserRole.USER,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshToken(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    family_id: Mapped[UUID | None] = mapped_column(index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_hash: Mapped[str | None] = mapped_column(String(64))
    device_info: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class ActionToken(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "action_tokens"
    __table_args__ = (
        Index("ix_action_tokens_user_purpose", "user_id", "purpose"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    purpose: Mapped[str] = mapped_column(String(40), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Subscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    plan: Mapped[Plan] = mapped_column(
        Enum(Plan, name="subscription_plan", values_callable=enum_values),
        default=Plan.FREE,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)


class PaymentWebhookEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Idempotency record for Stripe webhook processing."""

    __tablename__ = "payment_webhook_events"

    provider_event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(json_column_type(), default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)


class Paper(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "papers"
    __table_args__ = (
        Index("ix_papers_year_citations", "publication_year", "cited_by_count"),
        Index("ix_papers_open_access_year", "is_open_access", "publication_year"),
    )

    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date)
    publication_year: Mapped[int | None] = mapped_column(Integer, index=True)
    language: Mapped[str | None] = mapped_column(String(20), index=True)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    referenced_works_count: Mapped[int] = mapped_column(Integer, default=0)
    is_open_access: Mapped[bool] = mapped_column(Boolean, default=False)
    open_access_url: Mapped[str | None] = mapped_column(Text)
    pdf_url: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(255), index=True)
    type: Mapped[str | None] = mapped_column(String(80), index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(json_column_type(), default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dimension))


class Author(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "authors"

    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    orcid: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)
    works_count: Mapped[int] = mapped_column(Integer, default=0)


class Institution(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "institutions"

    openalex_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country_code: Mapped[str | None] = mapped_column(String(8), index=True)
    institution_type: Mapped[str | None] = mapped_column(String(80), index=True)


class PaperAuthor(Base):
    __tablename__ = "paper_authors"

    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    author_position: Mapped[str | None] = mapped_column(String(40))
    is_corresponding: Mapped[bool] = mapped_column(Boolean, default=False)


class PaperInstitution(Base):
    __tablename__ = "paper_institutions"

    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )


class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = (
        CheckConstraint("citing_paper_id <> cited_paper_id", name="no_self_citation"),
        Index("ix_citations_cited_paper", "cited_paper_id"),
    )

    citing_paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cited_paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Topic(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "topics"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dimension))


class PaperTopic(Base):
    __tablename__ = "paper_topics"

    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    topic_id: Mapped[UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, default=1.0)


class UserPaperInteraction(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_paper_interactions"
    __table_args__ = (
        CheckConstraint("interaction_value >= -10 AND interaction_value <= 10", name="valid_value"),
        Index("ix_interactions_user_created", "user_id", "created_at"),
        Index("ix_interactions_paper_type", "paper_id", "interaction_type"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        index=True,
    )
    interaction_type: Mapped[str] = mapped_column(String(40), index=True)
    interaction_value: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


class LibraryItem(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "library_items"
    __table_args__ = (
        UniqueConstraint("user_id", "paper_id", name="uq_library_user_paper"),
        Index("ix_library_user_collection", "user_id", "collection_name"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        index=True,
    )
    collection_name: Mapped[str] = mapped_column(String(100), default="Saved")
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(json_column_type(), default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    paper: Mapped[Paper] = relationship(lazy="selectin")


class UploadedDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "uploaded_documents"
    __table_args__ = (
        Index("ix_documents_user_status", "user_id", "processing_status"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)
    storage_path: Mapped[str] = mapped_column(Text)
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status", values_callable=enum_values),
        default=ProcessingStatus.PENDING,
        index=True,
    )
    processing_error: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)


class DocumentChunk(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_document_index"),
        Index("ix_document_chunks_document_page", "document_id", "page_number"),
    )

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("uploaded_documents.id", ondelete="CASCADE"),
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dimension))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(json_column_type(), default=dict)


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_sessions_user_updated", "user_id", "updated_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("uploaded_documents.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), default="New chat")


class ChatMessage(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(json_column_type(), default=list)
    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


class SearchHistory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "search_history"
    __table_args__ = (
        Index("ix_search_history_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    query: Mapped[str] = mapped_column(Text)
    filters: Mapped[dict[str, Any]] = mapped_column(json_column_type(), default=dict)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


class RecommendationLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recommendation_logs"
    __table_args__ = (
        Index("ix_recommendation_logs_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    paper_id: Mapped[UUID] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"),
        index=True,
    )
    algorithm: Mapped[str] = mapped_column(String(80))
    model_version: Mapped[str] = mapped_column(String(40), default="hybrid-v2")
    score: Mapped[float] = mapped_column(Float)
    components: Mapped[dict[str, float]] = mapped_column(json_column_type(), default=dict)
    explanation: Mapped[str] = mapped_column(Text)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    saved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
