from uuid import uuid4

from app.models.entities import DocumentChunk
from app.services.retrieval_service import RetrievedChunk, RetrievalService


def candidate(score: float, embedding: list[float], index: int) -> RetrievedChunk:
    chunk = DocumentChunk(
        id=uuid4(),
        document_id=uuid4(),
        page_number=index + 1,
        chunk_index=index,
        content=f"chunk {index}",
        token_count=2,
        embedding=embedding,
        metadata_json={},
    )
    return RetrievedChunk(
        chunk=chunk,
        vector_score=score,
        keyword_score=score,
        rerank_score=score,
        final_score=score,
        embedding=embedding,
    )


def test_mmr_keeps_relevance_but_avoids_near_duplicates() -> None:
    selected = RetrievalService._mmr_select(
        [
            candidate(0.95, [1.0, 0.0], 0),
            candidate(0.94, [0.999, 0.001], 1),
            candidate(0.80, [0.0, 1.0], 2),
        ],
        top_k=2,
        diversity_lambda=0.60,
    )
    assert selected[0].chunk.chunk_index == 0
    assert selected[1].chunk.chunk_index == 2
