from datetime import UTC, datetime
from uuid import uuid4

from app.models.entities import Paper
from app.services.embedding_service import get_embedding_service
from app.services.paper_search_service import PaperSearchService


class FakeReranker:
    def score(self, query: str, documents: list[str]) -> list[float]:
        return [1.0 if "retrieval" in document.lower() else 0.0 for document in documents]


def test_rank_combines_semantic_keyword_and_reranker(monkeypatch) -> None:
    service = get_embedding_service()
    service._model = False
    relevant_text = "Retrieval augmented generation retrieves evidence"
    irrelevant_text = "Marine biology and fish populations"
    relevant = Paper(
        id=uuid4(),
        title="Retrieval Augmented Generation",
        abstract=relevant_text,
        publication_year=datetime.now(UTC).year,
        cited_by_count=100,
        is_open_access=True,
        metadata_json={},
        embedding=service.encode_query(relevant_text),
    )
    irrelevant = Paper(
        id=uuid4(),
        title="Marine Biology",
        abstract=irrelevant_text,
        publication_year=2000,
        cited_by_count=1,
        is_open_access=False,
        metadata_json={},
        embedding=service.encode_query(irrelevant_text),
    )
    monkeypatch.setattr(
        "app.services.paper_search_service.get_reranking_service",
        lambda: FakeReranker(),
    )
    ranked = PaperSearchService()._rank(
        "retrieval generation",
        service.encode_query("retrieval generation"),
        [irrelevant, relevant],
    )
    assert ranked[0].paper.id == relevant.id
    assert ranked[0].components["rerank"] == 1.0
