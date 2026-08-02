import pytest

from app.services.llm_service import Message, OllamaLLM


def test_message_serialization_supports_slots_dataclass() -> None:
    message = Message(role="user", content="hello")
    assert message.to_payload() == {"role": "user", "content": "hello"}


@pytest.mark.asyncio
async def test_ollama_provider_uses_valid_message_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    async def fake_post(self, url: str, *, payload: dict, headers=None):
        captured.update(payload)
        return {"message": {"content": "grounded answer"}}

    monkeypatch.setattr(OllamaLLM, "_post_json", fake_post)
    monkeypatch.setattr("app.services.llm_service.settings.ollama_model", "test-model")
    response = await OllamaLLM().generate([Message("user", "question")])
    assert captured["messages"] == [{"role": "user", "content": "question"}]
    assert response.text == "grounded answer"
