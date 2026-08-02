from dataclasses import dataclass

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset

from app.ml.features.text_hashing import token_ids


@dataclass(slots=True, frozen=True)
class RelevanceExample:
    query: str
    title: str
    abstract: str
    label: float


class RelevanceDataset(Dataset):
    """Query-paper text-pair dataset for a lightweight neural relevance model."""

    def __init__(
        self,
        examples: list[RelevanceExample],
        *,
        vocab_size: int = 30_000,
        max_query_tokens: int = 48,
        max_document_tokens: int = 256,
    ) -> None:
        if not examples:
            raise ValueError("RelevanceDataset requires at least one example")
        self.examples = examples
        self.vocab_size = vocab_size
        self.max_query_tokens = max_query_tokens
        self.max_document_tokens = max_document_tokens

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        item = self.examples[index]
        document = f"{item.title}. {item.abstract}".strip()
        query = torch.tensor(
            token_ids(
                item.query,
                vocab_size=self.vocab_size,
                max_length=self.max_query_tokens,
            ),
            dtype=torch.long,
        )
        document_ids = torch.tensor(
            token_ids(
                document,
                vocab_size=self.vocab_size,
                max_length=self.max_document_tokens,
            ),
            dtype=torch.long,
        )
        label = torch.tensor(item.label, dtype=torch.float32)
        return query, document_ids, label


def collate_relevance_batch(
    batch: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    queries, documents, labels = zip(*batch, strict=True)
    return (
        pad_sequence(queries, batch_first=True, padding_value=0),
        pad_sequence(documents, batch_first=True, padding_value=0),
        torch.stack(labels),
    )
