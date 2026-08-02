import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
import yaml
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, random_split

from app.ml.datasets.relevance import (
    RelevanceDataset,
    RelevanceExample,
    collate_relevance_batch,
)
from app.ml.models.relevance_classifier import RelevanceClassifier


@dataclass(slots=True)
class TrainingConfig:
    data_path: str = "data/relevance_sample.json"
    output_path: str = "models/relevance.pt"
    seed: int = 42
    epochs: int = 30
    batch_size: int = 16
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    validation_fraction: float = 0.25
    patience: int = 5
    vocab_size: int = 30_000
    embedding_size: int = 96
    hidden_size: int = 128
    dropout: float = 0.20


def load_config(path: Path) -> TrainingConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return TrainingConfig(**raw)


def load_examples(path: Path) -> list[RelevanceExample]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [
        RelevanceExample(
            query=row["query"],
            title=row["title"],
            abstract=row.get("abstract", ""),
            label=float(row["label"]),
        )
        for row in rows
    ]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def evaluate(
    model: RelevanceClassifier,
    loader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device,
) -> dict[str, float | None]:
    model.eval()
    probabilities: list[float] = []
    labels: list[int] = []
    losses: list[float] = []
    with torch.no_grad():
        for query_ids, document_ids, targets in loader:
            query_ids = query_ids.to(device)
            document_ids = document_ids.to(device)
            targets = targets.to(device)
            logits = model(query_ids, document_ids)
            losses.append(float(loss_fn(logits, targets).item()))
            probabilities.extend(torch.sigmoid(logits).cpu().tolist())
            labels.extend(targets.int().cpu().tolist())
    predictions = [int(value >= 0.5) for value in probabilities]
    return {
        "loss": float(np.mean(losses)) if losses else 0.0,
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
        "roc_auc": roc_auc_score(labels, probabilities) if len(set(labels)) > 1 else None,
    }


def train(config: TrainingConfig) -> dict[str, float | None]:
    set_seed(config.seed)
    examples = load_examples(Path(config.data_path))
    dataset = RelevanceDataset(examples, vocab_size=config.vocab_size)
    validation_size = max(1, round(len(dataset) * config.validation_fraction))
    train_size = len(dataset) - validation_size
    if train_size < 1:
        raise ValueError("Training dataset must contain at least two examples")
    generator = torch.Generator().manual_seed(config.seed)
    train_set, validation_set = random_split(
        dataset,
        [train_size, validation_size],
        generator=generator,
    )
    train_loader = DataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collate_relevance_batch,
    )
    validation_loader = DataLoader(
        validation_set,
        batch_size=config.batch_size,
        collate_fn=collate_relevance_batch,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RelevanceClassifier(
        vocab_size=config.vocab_size,
        embedding_size=config.embedding_size,
        hidden_size=config.hidden_size,
        dropout=config.dropout,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    loss_fn = nn.BCEWithLogitsLoss()
    best_loss = float("inf")
    best_state: dict[str, torch.Tensor] | None = None
    remaining_patience = config.patience

    for epoch in range(1, config.epochs + 1):
        model.train()
        train_losses: list[float] = []
        for query_ids, document_ids, targets in train_loader:
            query_ids = query_ids.to(device)
            document_ids = document_ids.to(device)
            targets = targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(query_ids, document_ids)
            loss = loss_fn(logits, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_losses.append(float(loss.item()))

        metrics = evaluate(model, validation_loader, loss_fn, device)
        print(
            f"epoch={epoch} train_loss={np.mean(train_losses):.4f} "
            f"validation_loss={metrics['loss']:.4f} f1={metrics['f1']:.4f}"
        )
        validation_loss = float(metrics["loss"] or 0.0)
        if validation_loss < best_loss - 1e-4:
            best_loss = validation_loss
            best_state = {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()}
            remaining_patience = config.patience
        else:
            remaining_patience -= 1
            if remaining_patience == 0:
                print("Early stopping triggered")
                break

    if best_state is None:
        raise RuntimeError("Training did not produce a checkpoint")
    model.load_state_dict(best_state)
    final_metrics = evaluate(model, validation_loader, loss_fn, device)
    output_path = Path(config.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": best_state,
            "model_config": {
                "vocab_size": config.vocab_size,
                "embedding_size": config.embedding_size,
                "hidden_size": config.hidden_size,
                "dropout": config.dropout,
            },
            "training_config": asdict(config),
            "metrics": final_metrics,
        },
        output_path,
    )
    print(json.dumps(final_metrics, indent=2))
    return final_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/relevance.yaml"))
    args = parser.parse_args()
    train(load_config(args.config))
