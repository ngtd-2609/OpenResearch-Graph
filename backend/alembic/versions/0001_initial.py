"""Create the initial production-oriented OpenResearch schema.

Revision ID: 0001_initial
Revises: None
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = sa.Uuid()
JSONB = postgresql.JSONB(astext_type=sa.Text())
USER_ROLE = sa.Enum("user", "premium", "admin", name="user_role")
PLAN = sa.Enum("free", "premium", name="subscription_plan")
PROCESSING_STATUS = sa.Enum(
    "pending",
    "running",
    "completed",
    "failed",
    "canceled",
    name="processing_status",
)


def id_column() -> sa.Column:
    return sa.Column(
        "id",
        UUID,
        primary_key=True,
        nullable=False,
        server_default=sa.text("gen_random_uuid()"),
    )


def timestamp_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        id_column(),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(160)),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("role", USER_ROLE, nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        *timestamp_columns(),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "refresh_tokens",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("family_id", UUID),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by_hash", sa.String(64)),
        sa.Column("device_info", sa.String(255)),
        sa.Column("ip_address", sa.String(64)),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"])
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])

    op.create_table(
        "action_tokens",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("purpose", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("token_hash", name="uq_action_tokens_token_hash"),
    )
    op.create_index("ix_action_tokens_user_id", "action_tokens", ["user_id"])
    op.create_index("ix_action_tokens_token_hash", "action_tokens", ["token_hash"])
    op.create_index("ix_action_tokens_purpose", "action_tokens", ["purpose"])
    op.create_index("ix_action_tokens_expires_at", "action_tokens", ["expires_at"])
    op.create_index("ix_action_tokens_user_purpose", "action_tokens", ["user_id", "purpose"])

    op.create_table(
        "subscriptions",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", PLAN, nullable=False, server_default="free"),
        sa.Column("status", sa.String(40), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("stripe_subscription_id", sa.String(255)),
        sa.Column("current_period_start", sa.DateTime(timezone=True)),
        sa.Column("current_period_end", sa.DateTime(timezone=True)),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamp_columns(),
        sa.UniqueConstraint("user_id", name="uq_subscriptions_user_id"),
    )
    op.create_index("ix_subscriptions_plan", "subscriptions", ["plan"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"])
    op.create_index("ix_subscriptions_stripe_subscription_id", "subscriptions", ["stripe_subscription_id"])

    op.create_table(
        "payment_webhook_events",
        sa.Column("provider_event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_event_id", name="uq_payment_webhook_events_provider_event_id"),
    )
    op.create_index("ix_payment_webhook_events_provider_event_id", "payment_webhook_events", ["provider_event_id"])
    op.create_index("ix_payment_webhook_events_event_type", "payment_webhook_events", ["event_type"])
    op.create_index("ix_payment_webhook_events_processed", "payment_webhook_events", ["processed"])

    op.create_table(
        "papers",
        id_column(),
        sa.Column("openalex_id", sa.String(100)),
        sa.Column("doi", sa.String(255)),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract", sa.Text()),
        sa.Column("publication_date", sa.Date()),
        sa.Column("publication_year", sa.Integer()),
        sa.Column("language", sa.String(20)),
        sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referenced_works_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_open_access", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("open_access_url", sa.Text()),
        sa.Column("pdf_url", sa.Text()),
        sa.Column("source_name", sa.String(255)),
        sa.Column("type", sa.String(80)),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("embedding", Vector(384)),
        *timestamp_columns(),
        sa.UniqueConstraint("openalex_id", name="uq_papers_openalex_id"),
        sa.UniqueConstraint("doi", name="uq_papers_doi"),
    )
    for column in ("openalex_id", "doi", "publication_year", "language", "cited_by_count", "source_name", "type"):
        op.create_index(f"ix_papers_{column}", "papers", [column])
    op.create_index("ix_papers_year_citations", "papers", ["publication_year", "cited_by_count"])
    op.create_index("ix_papers_open_access_year", "papers", ["is_open_access", "publication_year"])
    op.execute(
        "CREATE INDEX ix_papers_full_text ON papers USING gin "
        "(to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(abstract, '')))"
    )
    op.execute(
        "CREATE INDEX ix_papers_embedding_hnsw ON papers USING hnsw "
        "(embedding vector_cosine_ops) WHERE embedding IS NOT NULL"
    )

    op.create_table(
        "authors",
        id_column(),
        sa.Column("openalex_id", sa.String(100)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("orcid", sa.String(100)),
        sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("works_count", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("openalex_id", name="uq_authors_openalex_id"),
        sa.UniqueConstraint("orcid", name="uq_authors_orcid"),
    )
    op.create_index("ix_authors_openalex_id", "authors", ["openalex_id"])
    op.create_index("ix_authors_name", "authors", ["name"])
    op.create_index("ix_authors_orcid", "authors", ["orcid"])

    op.create_table(
        "institutions",
        id_column(),
        sa.Column("openalex_id", sa.String(100)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country_code", sa.String(8)),
        sa.Column("institution_type", sa.String(80)),
        sa.UniqueConstraint("openalex_id", name="uq_institutions_openalex_id"),
    )
    for column in ("openalex_id", "name", "country_code", "institution_type"):
        op.create_index(f"ix_institutions_{column}", "institutions", [column])

    op.create_table(
        "topics",
        id_column(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("embedding", Vector(384)),
        sa.UniqueConstraint("name", name="uq_topics_name"),
    )
    op.create_index("ix_topics_name", "topics", ["name"])
    op.execute(
        "CREATE INDEX ix_topics_embedding_hnsw ON topics USING hnsw "
        "(embedding vector_cosine_ops) WHERE embedding IS NOT NULL"
    )

    op.create_table(
        "paper_authors",
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_id", UUID, sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_position", sa.String(40)),
        sa.Column("is_corresponding", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_paper_authors_author_id", "paper_authors", ["author_id"])

    op.create_table(
        "paper_institutions",
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("institution_id", UUID, sa.ForeignKey("institutions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_paper_institutions_institution_id", "paper_institutions", ["institution_id"])

    op.create_table(
        "paper_topics",
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("topic_id", UUID, sa.ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("score", sa.Float(), nullable=False, server_default="1"),
    )
    op.create_index("ix_paper_topics_topic_id", "paper_topics", ["topic_id"])

    op.create_table(
        "citations",
        sa.Column("citing_paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("cited_paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
        sa.CheckConstraint("citing_paper_id <> cited_paper_id", name="ck_citations_no_self_citation"),
    )
    op.create_index("ix_citations_cited_paper", "citations", ["cited_paper_id"])

    op.create_table(
        "user_paper_interactions",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_type", sa.String(40), nullable=False),
        sa.Column("interaction_value", sa.Float(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "interaction_value >= -10 AND interaction_value <= 10",
            name="ck_user_paper_interactions_valid_value",
        ),
    )
    op.create_index("ix_user_paper_interactions_user_id", "user_paper_interactions", ["user_id"])
    op.create_index("ix_user_paper_interactions_paper_id", "user_paper_interactions", ["paper_id"])
    op.create_index("ix_user_paper_interactions_interaction_type", "user_paper_interactions", ["interaction_type"])
    op.create_index("ix_interactions_user_created", "user_paper_interactions", ["user_id", "created_at"])
    op.create_index("ix_interactions_paper_type", "user_paper_interactions", ["paper_id", "interaction_type"])

    op.create_table(
        "library_items",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("collection_name", sa.String(100), nullable=False, server_default="Saved"),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "paper_id", name="uq_library_user_paper"),
    )
    op.create_index("ix_library_items_user_id", "library_items", ["user_id"])
    op.create_index("ix_library_items_paper_id", "library_items", ["paper_id"])
    op.create_index("ix_library_user_collection", "library_items", ["user_id", "collection_name"])

    op.create_table(
        "uploaded_documents",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("processing_status", PROCESSING_STATUS, nullable=False, server_default="pending"),
        sa.Column("processing_error", sa.Text()),
        sa.Column("page_count", sa.Integer()),
        *timestamp_columns(),
        sa.UniqueConstraint("stored_filename", name="uq_uploaded_documents_stored_filename"),
    )
    op.create_index("ix_uploaded_documents_user_id", "uploaded_documents", ["user_id"])
    op.create_index("ix_uploaded_documents_checksum", "uploaded_documents", ["checksum"])
    op.create_index("ix_uploaded_documents_processing_status", "uploaded_documents", ["processing_status"])
    op.create_index("ix_documents_user_status", "uploaded_documents", ["user_id", "processing_status"])

    op.create_table(
        "document_chunks",
        id_column(),
        sa.Column("document_id", UUID, sa.ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(384)),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_chunk_document_index"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_document_page", "document_chunks", ["document_id", "page_number"])
    op.execute(
        "CREATE INDEX ix_document_chunks_full_text ON document_chunks USING gin "
        "(to_tsvector('simple', content))"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw "
        "(embedding vector_cosine_ops) WHERE embedding IS NOT NULL"
    )

    op.create_table(
        "chat_sessions",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", UUID, sa.ForeignKey("uploaded_documents.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(255), nullable=False, server_default="New chat"),
        *timestamp_columns(),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])
    op.create_index("ix_chat_sessions_document_id", "chat_sessions", ["document_id"])
    op.create_index("ix_chat_sessions_user_updated", "chat_sessions", ["user_id", "updated_at"])

    op.create_table(
        "chat_messages",
        id_column(),
        sa.Column("session_id", UUID, sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("token_usage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])
    op.create_index("ix_chat_messages_session_created", "chat_messages", ["session_id", "created_at"])

    op.create_table(
        "search_history",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("filters", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])
    op.create_index("ix_search_history_user_created", "search_history", ["user_id", "created_at"])

    op.create_table(
        "recommendation_logs",
        id_column(),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paper_id", UUID, sa.ForeignKey("papers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("algorithm", sa.String(80), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False, server_default="hybrid-v2"),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("components", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("clicked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("saved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_recommendation_logs_user_id", "recommendation_logs", ["user_id"])
    op.create_index("ix_recommendation_logs_paper_id", "recommendation_logs", ["paper_id"])
    op.create_index("ix_recommendation_logs_user_created", "recommendation_logs", ["user_id", "created_at"])


def downgrade() -> None:
    for table in (
        "recommendation_logs",
        "search_history",
        "chat_messages",
        "chat_sessions",
        "document_chunks",
        "uploaded_documents",
        "library_items",
        "user_paper_interactions",
        "citations",
        "paper_topics",
        "paper_institutions",
        "paper_authors",
        "topics",
        "institutions",
        "authors",
        "papers",
        "subscriptions",
        "action_tokens",
        "refresh_tokens",
        "users",
    ):
        op.drop_table(table)
    PROCESSING_STATUS.drop(op.get_bind(), checkfirst=True)
    PLAN.drop(op.get_bind(), checkfirst=True)
    USER_ROLE.drop(op.get_bind(), checkfirst=True)
