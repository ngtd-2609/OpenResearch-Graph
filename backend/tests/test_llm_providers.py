from __future__ import annotations

from typing import Any

import pytest

from app.services import llm_service
from app.services.llm_service import (
    LLMProviderError,
    Message,
    MockLLM,
    OllamaLLM,
    OpenAICompatibleLLM,
)


@pytest.mark.asyncio
async def test_mock_llm_extracts_context_and_handles_empty_context() -> None:
    response = await MockLLM().generate([Message("user", "QUESTION: x\nCONTEXT: grounded text")])
    assert "grounded text" in response.text
    empty = await MockLLM().generate([])
    assert "Không tìm thấy" in empty.text


@pytest.mark.asyncio
async def test_ollama_validates_configuration_and_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_service.settings, "ollama_model", "")
    monkeypatch.setattr(llm_service.settings, "llm_model", "")
    with pytest.raises(LLMProviderError, match="not configured"):
        await OllamaLLM().generate([Message("user", "question")])

    monkeypatch.setattr(llm_service.settings, "ollama_model", "model")

    async def malformed(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {"wrong": True}

    monkeypatch.setattr(OllamaLLM, "_post_json", malformed)
    with pytest.raises(LLMProviderError, match="Unexpected Ollama"):
        await OllamaLLM().generate([Message("user", "question")])


@pytest.mark.asyncio
async def test_openai_compatible_provider_validates_and_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_service.settings, "llm_api_key", "")
    monkeypatch.setattr(llm_service.settings, "llm_base_url", "")
    monkeypatch.setattr(llm_service.settings, "llm_model", "")
    with pytest.raises(LLMProviderError, match="not fully configured"):
        await OpenAICompatibleLLM().generate([Message("user", "question")])

    monkeypatch.setattr(llm_service.settings, "llm_api_key", "key")
    monkeypatch.setattr(llm_service.settings, "llm_base_url", "https://provider.example/v1")
    monkeypatch.setattr(llm_service.settings, "llm_model", "small-model")
    captured: dict[str, Any] = {}

    async def valid(_self: Any, url: str, *, payload: dict[str, Any], headers=None):
        captured.update({"url": url, "payload": payload, "headers": headers})
        return {"choices": [{"message": {"content": "answer"}}]}

    monkeypatch.setattr(OpenAICompatibleLLM, "_post_json", valid)
    response = await OpenAICompatibleLLM().generate([Message("user", "question")])
    assert response.text == "answer"
    assert captured["headers"]["Authorization"] == "Bearer key"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "question"}]


@pytest.mark.asyncio
async def test_http_json_provider_retries_and_wraps_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0

    class Response:
        def raise_for_status(self) -> None:
            raise llm_service.httpx.HTTPStatusError(
                "failed", request=llm_service.httpx.Request("POST", "https://example"),
                response=llm_service.httpx.Response(503),
            )

        def json(self) -> dict[str, Any]:
            return {}

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args: Any) -> None:
            return None

        async def post(self, *_args: Any, **_kwargs: Any) -> Response:
            nonlocal attempts
            attempts += 1
            return Response()

    monkeypatch.setattr(llm_service.httpx, "AsyncClient", lambda **_kwargs: Client())
    monkeypatch.setattr(llm_service.settings, "llm_max_retries", 1)
    monkeypatch.setattr(llm_service.asyncio, "sleep", lambda _seconds: _completed())
    with pytest.raises(LLMProviderError, match="request failed"):
        await OllamaLLM()._post_json("https://example", payload={})
    assert attempts == 2


async def _completed() -> None:
    return None


def test_provider_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_service.settings, "llm_provider", "unknown")
    with pytest.raises(LLMProviderError, match="Unsupported"):
        llm_service.get_llm_provider()
