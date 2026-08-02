from pathlib import Path

import torch

from app.ml.datasets.relevance import RelevanceDataset, RelevanceExample, collate_relevance_batch
from app.ml.models.relevance_classifier import RelevanceClassifier


class RelevanceInferenceService:
    def __init__(self, checkpoint_path: Path) -> None:
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        model_config = checkpoint["model_config"]
        self.model = RelevanceClassifier(**model_config)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
        self.vocab_size = int(model_config["vocab_size"])

    def score(self, query: str, title: str, abstract: str = "") -> float:
        dataset = RelevanceDataset(
            [RelevanceExample(query=query, title=title, abstract=abstract, label=0.0)],
            vocab_size=self.vocab_size,
        )
        query_ids, document_ids, _ = collate_relevance_batch([dataset[0]])
        with torch.no_grad():
            return float(self.model.predict_proba(query_ids, document_ids).item())
