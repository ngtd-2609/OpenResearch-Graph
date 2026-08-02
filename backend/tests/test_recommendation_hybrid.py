from uuid import uuid4

from app.services.recommendation_service import RecommendationService


def test_profile_vector_is_normalized_and_weighted() -> None:
    first, second = uuid4(), uuid4()
    profile = RecommendationService._build_profile_vector(
        {first: 2.0, second: 1.0},
        {first: [1.0, 0.0], second: [0.0, 1.0]},
    )
    assert profile is not None
    assert profile[0] > profile[1]
    assert abs(sum(value * value for value in profile) - 1.0) < 1e-5


def test_collaborative_and_graph_components_affect_final_score(monkeypatch) -> None:
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_content_weight", 0.0)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_collaborative_weight", 0.5)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_graph_weight", 0.5)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_popularity_weight", 0.0)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_recency_weight", 0.0)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_open_access_weight", 0.0)
    monkeypatch.setattr("app.services.recommendation_service.settings.recommendation_feedback_weight", 0.0)
    assert RecommendationService._weighted_score(
        {
            "content": 0.0,
            "collaborative": 0.8,
            "graph": 0.6,
            "popularity": 0.0,
            "recency": 0.0,
            "open_access": 0.0,
            "feedback": 0.0,
        }
    ) == 0.7
