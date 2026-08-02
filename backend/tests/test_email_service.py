from email.message import EmailMessage

import pytest

from app.services.email_service import EmailService


@pytest.mark.asyncio
async def test_console_email_does_not_open_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.email_service.settings.email_backend", "console")
    called = False

    def fail(_message: EmailMessage) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(EmailService, "_send_smtp", staticmethod(fail))
    await EmailService().send_action_link("student@example.com", "Verify", "https://example.com/token")
    assert called is False


@pytest.mark.asyncio
async def test_smtp_email_is_built_without_exposing_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.email_service.settings.email_backend", "smtp")
    captured: list[EmailMessage] = []

    def capture(message: EmailMessage) -> None:
        captured.append(message)

    monkeypatch.setattr(EmailService, "_send_smtp", staticmethod(capture))
    await EmailService().send_action_link("student@example.com", "Reset password", "https://example.com/reset")
    assert captured[0]["To"] == "student@example.com"
    assert "https://example.com/reset" in captured[0].get_content()
