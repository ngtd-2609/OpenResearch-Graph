import pytest

from app.services.reranking_service import RerankingService


def test_lexical_reranker_rewards_query_coverage() -> None:
    service = RerankingService()
    service._model = False
    scores = service.score(
        "graph neural network",
        ["graph neural network methods", "unrelated classical statistics"],
    )
    assert scores[0] > scores[1]
    assert 0 <= scores[0] <= 1


def test_cross_encoder_scores_are_mapped_through_sigmoid() -> None:
    class Model:
        def predict(self, _pairs):
            return [2.0, -2.0]

    service = RerankingService()
    service._model = Model()
    scores = service.score("query", ["positive", "negative"])
    assert scores[0] == pytest.approx(0.8808, rel=1e-3)
    assert scores[1] == pytest.approx(0.1192, rel=1e-3)


def test_empty_documents_do_not_load_model() -> None:
    service = RerankingService()
    assert service.score("query", []) == []
    assert service._model is None
