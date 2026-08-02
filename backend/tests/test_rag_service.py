from uuid import uuid4

import pytest

from app.models.entities import DocumentChunk
from app.services.llm_service import LLMResponse
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievedChunk


class FakeProvider:
    async def generate(self, messages):
        assert "SOURCE" in messages[-1].content
        return LLMResponse(text="Câu trả lời có căn cứ.", model="fake")


@pytest.mark.asyncio
async def test_rag_returns_page_level_citations(monkeypatch) -> None:
    document_id = uuid4()
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=document_id,
        page_number=3,
        chunk_index=0,
        content="The method retrieves passages before generation.",
        token_count=7,
        embedding=[1.0, 0.0],
        metadata_json={},
    )

    async def fake_retrieve(self, db, *, document_id, query, top_k):
        return [
            RetrievedChunk(
                chunk=chunk,
                vector_score=0.9,
                keyword_score=0.8,
                rerank_score=0.95,
                final_score=0.91,
                embedding=[1.0, 0.0],
            )
        ]

    monkeypatch.setattr("app.services.rag_service.RetrievalService.retrieve", fake_retrieve)
    monkeypatch.setattr("app.services.rag_service.get_llm_provider", lambda: FakeProvider())
    response = await RAGService().answer(object(), document_id, "What is the method?")
    assert response.model == "fake"
    assert response.citations[0].page == 3
    assert response.citations[0].score == 0.91
