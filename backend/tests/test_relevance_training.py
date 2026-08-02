from pathlib import Path

from app.ml.inference.relevance import RelevanceInferenceService
from app.ml.training.train_relevance import TrainingConfig, train


def test_training_creates_reloadable_checkpoint(tmp_path: Path) -> None:
    source = Path(__file__).parents[1] / "data" / "relevance_sample.json"
    checkpoint = tmp_path / "relevance.pt"
    metrics = train(
        TrainingConfig(
            data_path=str(source),
            output_path=str(checkpoint),
            epochs=2,
            batch_size=8,
            patience=2,
            vocab_size=1_000,
            embedding_size=16,
            hidden_size=16,
        )
    )
    assert checkpoint.exists()
    assert 0 <= float(metrics["f1"] or 0) <= 1
    score = RelevanceInferenceService(checkpoint).score(
        "retrieval augmented generation",
        "Grounded document retrieval",
        "The system retrieves evidence before answering.",
    )
    assert 0 <= score <= 1
