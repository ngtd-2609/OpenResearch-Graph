import torch
from torch import nn
from torch.nn import functional as F


class RelevanceClassifier(nn.Module):
    """Siamese text encoder for query-paper relevance.

    It is deliberately small enough for a student laptop while still learning
    token embeddings directly from query, title and abstract text.
    """

    def __init__(
        self,
        *,
        vocab_size: int = 30_000,
        embedding_size: int = 96,
        hidden_size: int = 128,
        dropout: float = 0.20,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding = nn.Embedding(vocab_size, embedding_size, padding_idx=0)
        feature_size = embedding_size * 4 + 1
        self.classifier = nn.Sequential(
            nn.Linear(feature_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
        )

    def _mean_pool(self, token_ids: torch.Tensor) -> torch.Tensor:
        mask = token_ids.ne(0).unsqueeze(-1)
        embedded = self.embedding(token_ids)
        summed = (embedded * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp_min(1)
        return summed / counts

    def forward(self, query_ids: torch.Tensor, document_ids: torch.Tensor) -> torch.Tensor:
        query = self._mean_pool(query_ids)
        document = self._mean_pool(document_ids)
        cosine = F.cosine_similarity(query, document).unsqueeze(1)
        features = torch.cat(
            [query, document, torch.abs(query - document), query * document, cosine],
            dim=1,
        )
        return self.classifier(features).squeeze(1)

    def predict_proba(self, query_ids: torch.Tensor, document_ids: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self(query_ids, document_ids))
