from types import SimpleNamespace

import pytest

from app.services.payment_service import PaymentConfigurationError, PaymentService


@pytest.mark.asyncio
async def test_mock_checkout_never_requires_stripe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.payment_service.settings.billing_mode", "mock")
    result = await PaymentService().create_checkout("user-1", "user@example.com")
    assert result["mode"] == "mock"
    assert "mock_upgrade=1" in result["checkout_url"]


def test_stripe_mode_rejects_incomplete_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.payment_service.settings.billing_mode", "stripe")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_secret_key", "")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_webhook_secret", "")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_price_premium_monthly", "")
    with pytest.raises(PaymentConfigurationError, match="Missing Stripe settings"):
        PaymentService()


@pytest.mark.asyncio
async def test_checkout_runs_sync_stripe_sdk_off_event_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.payment_service.settings.billing_mode", "stripe")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_secret_key", "sk_test_x")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_webhook_secret", "whsec_x")
    monkeypatch.setattr("app.services.payment_service.settings.stripe_price_premium_monthly", "price_x")

    captured: dict = {}

    class Session:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(url="https://checkout.example/session")

    fake_stripe = SimpleNamespace(
        api_key="",
        checkout=SimpleNamespace(Session=Session),
        billing_portal=SimpleNamespace(Session=Session),
        Webhook=SimpleNamespace(construct_event=lambda body, signature, secret: {}),
    )
    monkeypatch.setattr("app.services.payment_service.stripe", fake_stripe)

    result = await PaymentService().create_checkout("user-1", "user@example.com")
    assert result == {"mode": "stripe", "checkout_url": "https://checkout.example/session"}
    assert captured["metadata"] == {"user_id": "user-1"}
    assert captured["line_items"][0]["price"] == "price_x"
