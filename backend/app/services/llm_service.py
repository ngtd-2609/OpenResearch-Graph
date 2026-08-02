import asyncio
from dataclasses import asdict, dataclass
from typing import Any, Protocol

import httpx

from app.core.config import settings


class LLMProviderError(RuntimeError):
    """Raised when an external LLM provider cannot produce a valid response."""


@dataclass(slots=True, frozen=True)
class Message:
    role: str
    content: str

    def to_payload(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class LLMResponse:
    text: str
    model: str


class LLMProvider(Protocol):
    async def generate(self, messages: list[Message]) -> LLMResponse: ...


class MockLLM:
    """Deterministic extractive fallback used for local development and tests."""

    async def generate(self, messages: list[Message]) -> LLMResponse:
        user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        context = user_message.split("CONTEXT:", 1)[-1].strip()
        excerpt = context[:1_800].strip()
        if not excerpt:
            excerpt = "Không tìm thấy ngữ cảnh phù hợp trong tài liệu."
        return LLMResponse(
            text=(
                "Đây là câu trả lời ở chế độ mock/extractive. "
                "Dựa trên các đoạn được truy xuất:\n\n" + excerpt
            ),
            model="mock-extractive",
        )


class _HTTPJSONProvider:
    async def _post_json(
        self,
        url: str,
        *,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        timeout = httpx.Timeout(settings.llm_timeout_seconds)
        for attempt in range(settings.llm_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    if not isinstance(data, dict):
                        raise LLMProviderError("LLM provider returned a non-object JSON response")
                    return data
            except (httpx.HTTPError, ValueError, LLMProviderError) as exc:
                last_error = exc
                if attempt < settings.llm_max_retries:
                    await asyncio.sleep(0.5 * (2**attempt))
        raise LLMProviderError(f"LLM provider request failed: {last_error}") from last_error


class OllamaLLM(_HTTPJSONProvider):
    async def generate(self, messages: list[Message]) -> LLMResponse:
        model = settings.ollama_model or settings.llm_model
        if not model:
            raise LLMProviderError("Ollama model is not configured")
        data = await self._post_json(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            payload={
                "model": model,
                "messages": [message.to_payload() for message in messages],
                "stream": False,
            },
        )
        try:
            text = str(data["message"]["content"]).strip()
        except (KeyError, TypeError) as exc:
            raise LLMProviderError("Unexpected Ollama response schema") from exc
        if not text:
            raise LLMProviderError("Ollama returned an empty answer")
        return LLMResponse(text=text, model=model)


class OpenAICompatibleLLM(_HTTPJSONProvider):
    async def generate(self, messages: list[Message]) -> LLMResponse:
        if not settings.llm_api_key or not settings.llm_base_url or not settings.llm_model:
            raise LLMProviderError("OpenAI-compatible provider is not fully configured")
        data = await self._post_json(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            payload={
                "model": settings.llm_model,
                "messages": [message.to_payload() for message in messages],
                "temperature": 0.1,
            },
        )
        try:
            text = str(data["choices"][0]["message"]["content"]).strip()
        except (IndexError, KeyError, TypeError) as exc:
            raise LLMProviderError("Unexpected OpenAI-compatible response schema") from exc
        if not text:
            raise LLMProviderError("OpenAI-compatible provider returned an empty answer")
        return LLMResponse(text=text, model=settings.llm_model)


def get_llm_provider() -> LLMProvider:
    providers: dict[str, type[LLMProvider]] = {
        "mock": MockLLM,
        "ollama": OllamaLLM,
        "openai-compatible": OpenAICompatibleLLM,
    }
    provider_class = providers.get(settings.llm_provider)
    if provider_class is None:
        raise LLMProviderError(f"Unsupported LLM provider: {settings.llm_provider}")
    return provider_class()
