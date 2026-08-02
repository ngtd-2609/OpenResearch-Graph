import logging
import math
import re
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)
TOKEN_PATTERN = re.compile(r"[\w-]+", re.UNICODE)


class RerankingService:
    """Optional cross-encoder reranker with a deterministic lexical fallback."""

    def __init__(self) -> None:
        self._model: object | bool | None = None

    def _load_model(self) -> object | bool:
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(settings.reranker_model_name, device=settings.embedding_device)
            except Exception as exc:  # pragma: no cover - environment dependent
                logger.warning("Cross-encoder unavailable; using lexical reranker: %s", exc)
                self._model = False
        return self._model

    def score(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []
        model = self._load_model()
        if model:
            raw_scores = model.predict([(query, document) for document in documents])
            return [self._sigmoid(float(score)) for score in raw_scores]
        query_terms = set(TOKEN_PATTERN.findall(query.lower()))
        scores: list[float] = []
        for document in documents:
            document_terms = set(TOKEN_PATTERN.findall(document.lower()))
            overlap = len(query_terms & document_terms) / max(len(query_terms), 1)
            coverage = len(query_terms & document_terms) / max(len(document_terms), 1)
            scores.append(min(1.0, 0.8 * overlap + 0.2 * coverage))
        return scores

    @staticmethod
    def _sigmoid(value: float) -> float:
        if value >= 0:
            return 1.0 / (1.0 + math.exp(-value))
        exponent = math.exp(value)
        return exponent / (1.0 + exponent)


@lru_cache
def get_reranking_service() -> RerankingService:
    return RerankingService()
