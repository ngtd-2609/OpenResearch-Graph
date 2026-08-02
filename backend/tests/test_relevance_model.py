import torch

from app.ml.datasets.relevance import (
    RelevanceDataset,
    RelevanceExample,
    collate_relevance_batch,
)
from app.ml.models.relevance_classifier import RelevanceClassifier


def test_text_pair_model_accepts_query_title_abstract() -> None:
    dataset = RelevanceDataset(
        [
            RelevanceExample(
                query="retrieval augmented generation",
                title="Grounded RAG",
                abstract="Retrieval supports answers with evidence.",
                label=1.0,
            ),
            RelevanceExample(
                query="retrieval augmented generation",
                title="Crop disease detection",
                abstract="A vision model classifies leaves.",
                label=0.0,
            ),
        ],
        vocab_size=1_000,
    )
    query_ids, document_ids, labels = collate_relevance_batch([dataset[0], dataset[1]])
    model = RelevanceClassifier(vocab_size=1_000, embedding_size=16, hidden_size=16)
    logits = model(query_ids, document_ids)
    probabilities = torch.sigmoid(logits)
    assert logits.shape == (2,)
    assert labels.shape == (2,)
    assert torch.all((probabilities >= 0) & (probabilities <= 1))
