from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1 import subscriptions
from app.models.entities import PaymentWebhookEvent, Plan, Subscription, User, UserRole
from app.services.payment_service import PaymentConfigurationError


class FakeDb:
    def __init__(
        self,
        *,
        scalar_values: list[Any] | None = None,
        objects: dict[tuple[type, object], Any] | None = None,
    ) -> None:
        self.scalar_values = scalar_values or []
        self.objects = objects or {}
        self.added: list[Any] = []
        self.commit_count = 0

    async def scalar(self, _statement: Any) -> Any:
        return self.scalar_values.pop(0) if self.scalar_values else None

    async def get(self, model: type, key: object) -> Any:
        return self.objects.get((model, key))

    def add(self, item: Any) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid4()
        self.added.append(item)

    async def commit(self) -> None:
        self.commit_count += 1


def make_user() -> User:
    return User(
        id=uuid4(), email="user@example.com", username="user", password_hash="hash",
        role=UserRole.USER, is_active=True,
    )


def request(body: bytes = b"{}") -> Request:
    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(
        {
            "type": "http", "method": "POST", "path": "/webhook", "headers": [],
            "query_string": b"", "client": ("127.0.0.1", 1), "server": ("test", 80),
            "scheme": "http",
        },
        receive=receive,
    )


@pytest.mark.asyncio
async def test_subscription_summary_and_mock_upgrade(monkeypatch: pytest.MonkeyPatch) -> None:
    user = make_user()
    empty = await subscriptions.my_subscription(user, FakeDb())  # type: ignore[arg-type]
    assert empty["plan"] == "free"

    subscription = Subscription(user_id=user.id, plan=Plan.PREMIUM, status="active")
    summary = await subscriptions.my_subscription(user, FakeDb(scalar_values=[subscription]))  # type: ignore[arg-type]
    assert summary["plan"] == "premium"

    monkeypatch.setattr(subscriptions.settings, "billing_mode", "mock")
    db = FakeDb(scalar_values=[None])
    result = await subscriptions.mock_upgrade(user, db)  # type: ignore[arg-type]
    assert result["message"].startswith("Development")
    assert user.role == UserRole.PREMIUM
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_mock_upgrade_is_disabled_in_stripe_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subscriptions.settings, "billing_mode", "stripe")
    with pytest.raises(HTTPException) as exc:
        await subscriptions.mock_upgrade(make_user(), FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_checkout_and_portal_translate_configuration_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_checkout(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise PaymentConfigurationError("Missing Stripe settings")

    async def fail_portal(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise ValueError("No Stripe customer")

    monkeypatch.setattr(subscriptions.PaymentService, "create_checkout", fail_checkout)
    with pytest.raises(HTTPException) as exc:
        await subscriptions.checkout(make_user())
    assert exc.value.status_code == 503

    monkeypatch.setattr(subscriptions.PaymentService, "create_portal", fail_portal)
    with pytest.raises(HTTPException) as exc:
        await subscriptions.portal(make_user(), FakeDb(scalar_values=[None]))  # type: ignore[arg-type]
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_webhook_mock_mode_is_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subscriptions.settings, "billing_mode", "mock")
    result = await subscriptions.stripe_webhook(request(), "", FakeDb())  # type: ignore[arg-type]
    assert result == {"received": True, "mode": "mock"}


@pytest.mark.asyncio
async def test_checkout_webhook_is_idempotent_and_activates_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subscriptions.settings, "billing_mode", "stripe")
    monkeypatch.setattr(subscriptions.settings, "stripe_secret_key", "sk_test_x")
    monkeypatch.setattr(subscriptions.settings, "stripe_webhook_secret", "whsec_x")
    monkeypatch.setattr(subscriptions.settings, "stripe_price_premium_monthly", "price_x")
    user = make_user()
    event = {
        "id": "evt_checkout",
        "type": "checkout.session.completed",
        "data": {"object": {
            "customer": "cus_1", "subscription": "sub_1",
            "metadata": {"user_id": str(user.id)},
        }},
    }
    monkeypatch.setattr(
        subscriptions.PaymentService,
        "construct_event",
        lambda _self, _body, _signature: event,
    )
    db = FakeDb(scalar_values=[None, None], objects={(User, user.id): user})
    result = await subscriptions.stripe_webhook(request(), "sig", db)  # type: ignore[arg-type]
    assert result["duplicate"] is False
    assert user.role == UserRole.PREMIUM
    assert any(isinstance(item, PaymentWebhookEvent) for item in db.added)
    assert any(isinstance(item, Subscription) for item in db.added)

    processed = PaymentWebhookEvent(
        provider_event_id="evt_checkout", event_type="checkout.session.completed",
        payload_json={}, processed=True,
    )
    duplicate_db = FakeDb(scalar_values=[processed])
    duplicate = await subscriptions.stripe_webhook(request(), "sig", duplicate_db)  # type: ignore[arg-type]
    assert duplicate["duplicate"] is True


@pytest.mark.asyncio
async def test_subscription_deactivation_updates_plan_and_role() -> None:
    user = make_user()
    user.role = UserRole.PREMIUM
    subscription = Subscription(
        user_id=user.id, plan=Plan.PREMIUM, status="active",
        stripe_subscription_id="sub_1",
    )
    db = FakeDb(scalar_values=[subscription], objects={(User, user.id): user})
    await subscriptions._deactivate_subscription(db, "sub_1")  # type: ignore[arg-type]
    assert subscription.plan == Plan.FREE
    assert subscription.status == "canceled"
    assert user.role == UserRole.USER
