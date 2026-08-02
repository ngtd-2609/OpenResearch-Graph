import os

import pytest
from sqlalchemy import text

from app.db.session import engine

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_TESTS") != "1",
    reason="Set RUN_DB_TESTS=1 to run PostgreSQL integration tests",
)


@pytest.mark.asyncio
async def test_required_extensions_and_indexes_exist() -> None:
    async with engine.connect() as connection:
        extensions = {
            row[0]
            for row in (
                await connection.execute(
                    text("SELECT extname FROM pg_extension WHERE extname IN ('vector', 'pgcrypto')")
                )
            ).all()
        }
        assert extensions == {"vector", "pgcrypto"}

        indexes = {
            row[0]
            for row in (
                await connection.execute(
                    text(
                        "SELECT indexname FROM pg_indexes "
                        "WHERE indexname IN ("
                        "'ix_papers_full_text', 'ix_papers_embedding_hnsw', "
                        "'ix_document_chunks_embedding_hnsw')"
                    )
                )
            ).all()
        }
        assert indexes == {
            "ix_papers_full_text",
            "ix_papers_embedding_hnsw",
            "ix_document_chunks_embedding_hnsw",
        }
