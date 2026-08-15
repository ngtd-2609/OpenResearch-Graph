import hashlib
import logging
import re
from functools import lru_cache
from typing import Iterable

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)
TOKEN_PATTERN = re.compile(r"[\w-]+", re.UNICODE)


class EmbeddingService:
    """Sentence embedding facade with a deterministic offline fallback.

    The fallback is intentionally stable across processes, which makes local
    tests and seed-mode search reproducible without downloading a model.
    """

    def __init__(self) -> None:
        self._model: object | bool | None = None
        self.backend_name = "not-loaded"

    def _load_model(self) -> object | bool:
        if self._model is None:
            try:
                import os
                import torch
                from sentence_transformers import SentenceTransformer

                # Set optimal thread count for CPU parallel vectorization
                threads = min(8, max(2, os.cpu_count() or 4))
                torch.set_num_threads(threads)

                model = SentenceTransformer(
                    settings.embedding_model_name,
                    device=settings.embedding_device,
                )
                dimension = int(model.get_sentence_embedding_dimension())
                if dimension != settings.embedding_dimension:
                    raise ValueError(
                        f"Embedding dimension mismatch: model={dimension}, "
                        f"configured={settings.embedding_dimension}"
                    )
                self._model = model
                self.backend_name = settings.embedding_model_name
            except Exception as exc:  # pragma: no cover - environment dependent
                logger.warning("Falling back to deterministic hash embeddings: %s", exc)
                self._model = False
                self.backend_name = "deterministic-hash"
        return self._model

    def encode(self, texts: Iterable[str], *, batch_size: int = 64) -> list[list[float]]:
        normalized_texts = [text.strip() for text in texts]
        if not normalized_texts:
            return []
        model = self._load_model()
        if model:
            try:
                import torch

                with torch.inference_mode():
                    vectors = model.encode(
                        normalized_texts,
                        normalize_embeddings=True,
                        batch_size=batch_size,
                        show_progress_bar=False,
                    )
            except Exception:
                vectors = model.encode(
                    normalized_texts,
                    normalize_embeddings=True,
                    batch_size=batch_size,
                    show_progress_bar=False,
                )
            return [np.asarray(vector, dtype=np.float32).astype(float).tolist() for vector in vectors]
        return [self._hash_embedding(text) for text in normalized_texts]

    @lru_cache(maxsize=2048)
    def encode_query_cached(self, text: str) -> tuple[float, ...]:
        return tuple(self.encode([text])[0])

    def encode_query(self, text: str) -> list[float]:
        return list(self.encode_query_cached(text))

    def _hash_embedding(self, text: str) -> list[float]:
        vector = np.zeros(settings.embedding_dimension, dtype=np.float32)
        for token in TOKEN_PATTERN.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % settings.embedding_dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = float(np.linalg.norm(vector)) or 1.0
        return (vector / norm).astype(float).tolist()

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        left_array = np.asarray(left, dtype=np.float32)
        right_array = np.asarray(right, dtype=np.float32)
        denominator = float(np.linalg.norm(left_array) * np.linalg.norm(right_array))
        if denominator == 0:
            return 0.0
        return float(np.dot(left_array, right_array) / denominator)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
