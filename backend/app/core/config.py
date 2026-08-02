from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Defaults intentionally support a local development setup. Production mode
    validates that placeholder secrets and unsafe debug settings are not used.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "OpenResearch Graph"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = True
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] | str = ["http://localhost:3000"]

    database_url: str = (
        "postgresql+asyncpg://openresearch_user:change_this_in_production"
        "@localhost:5432/openresearch"
    )
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "replace_with_a_long_random_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    login_attempts_per_15_minutes: int = 10

    openalex_mode: Literal["seed", "api"] = "seed"
    openalex_api_key: str = ""
    openalex_email: str = ""  # polite pool: mailto= param, no account required
    openalex_base_url: str = "https://api.openalex.org"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    embedding_device: str = "cpu"
    embedding_dimension: int = 384

    llm_provider: Literal["mock", "ollama", "openai-compatible"] = "mock"
    llm_model: str = ""
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_timeout_seconds: float = 120.0
    llm_max_retries: int = 2
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""

    billing_mode: Literal["mock", "stripe"] = "mock"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_premium_monthly: str = ""

    email_backend: Literal["console", "smtp", "mailpit"] = "console"
    email_from: str = "noreply@example.com"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = False

    storage_backend: Literal["local", "s3-compatible"] = "local"
    local_storage_path: str = "./uploads"
    s3_endpoint_url: str = ""
    s3_bucket: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_region: str = "auto"

    max_upload_size_mb: int = 25
    max_free_documents: int = 3
    max_premium_documents: int = 50
    max_free_chat_messages_per_day: int = 20
    free_searches_per_hour: int = 20
    premium_searches_per_hour: int = 200

    search_candidate_pool: int = 300
    search_keyword_weight: float = 0.30
    search_semantic_weight: float = 0.35
    search_citation_weight: float = 0.15
    search_recency_weight: float = 0.10
    search_open_access_weight: float = 0.05
    search_rerank_weight: float = 0.05

    rag_candidate_pool: int = 30
    rag_top_k: int = 6
    rag_max_context_chars: int = 12_000
    rag_mmr_lambda: float = 0.75

    recommendation_candidate_pool: int = 500
    recommendation_content_weight: float = 0.35
    recommendation_collaborative_weight: float = 0.20
    recommendation_graph_weight: float = 0.15
    recommendation_popularity_weight: float = 0.12
    recommendation_recency_weight: float = 0.10
    recommendation_open_access_weight: float = 0.03
    recommendation_feedback_weight: float = 0.05
    recommendation_diversity_lambda: float = 0.80

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> "Settings":
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be false in production")
            if self.jwt_secret_key == "replace_with_a_long_random_secret":
                raise ValueError("JWT_SECRET_KEY must be replaced in production")
            if any(origin == "*" for origin in self.cors_origins):
                raise ValueError("Wildcard CORS is not allowed in production")
        if self.llm_provider == "ollama" and not (self.ollama_model or self.llm_model):
            raise ValueError("OLLAMA_MODEL or LLM_MODEL is required for Ollama")
        if self.llm_provider == "openai-compatible":
            if not self.llm_base_url or not self.llm_model or not self.llm_api_key:
                raise ValueError(
                    "LLM_BASE_URL, LLM_MODEL and LLM_API_KEY are required for openai-compatible"
                )
        return self

    @property
    def upload_limit_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def search_weights(self) -> dict[str, float]:
        weights = {
            "keyword": self.search_keyword_weight,
            "semantic": self.search_semantic_weight,
            "citation": self.search_citation_weight,
            "recency": self.search_recency_weight,
            "open_access": self.search_open_access_weight,
            "rerank": self.search_rerank_weight,
        }
        total = sum(weights.values()) or 1.0
        return {name: value / total for name, value in weights.items()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
