import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_placeholder_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            debug=False,
            jwt_secret_key="replace_with_a_long_random_secret",
            cors_origins=["https://example.com"],
            _env_file=None,
        )


def test_production_accepts_safe_minimum() -> None:
    settings = Settings(
        environment="production",
        debug=False,
        jwt_secret_key="a" * 64,
        cors_origins=["https://example.com"],
    )
    assert settings.environment == "production"
