from app.services.embedding_service import EmbeddingService


def test_hash_embeddings_are_deterministic_and_normalized() -> None:
    service = EmbeddingService()
    service._model = False
    first, second = service.encode(["research graph", "research graph"])
    assert first == second
    assert abs(sum(value * value for value in first) - 1.0) < 1e-5
    assert service.cosine_similarity(first, second) > 0.999
