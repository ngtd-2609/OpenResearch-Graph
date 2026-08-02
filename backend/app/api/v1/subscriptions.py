from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import (
    PaymentWebhookEvent,
    Plan,
    Subscription,
    User,
    UserRole,
)
from app.services.payment_service import PaymentConfigurationError, PaymentService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


async def _subscription_for_user(db: AsyncSession, user_id: UUID) -> Subscription | None:
    return await db.scalar(select(Subscription).where(Subscription.user_id == user_id))


@router.get("/me")
async def my_subscription(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    item = await _subscription_for_user(db, user.id)
    if item is None:
        return {"plan": "free", "status": "inactive", "current_period_end": None}
    return {
        "id": str(item.id),
        "plan": item.plan.value,
        "status": item.status,
        "current_period_end": item.current_period_end,
        "cancel_at_period_end": item.cancel_at_period_end,
    }


@router.post("/checkout")
async def checkout(user: User = Depends(current_user)) -> dict[str, Any]:
    try:
        return await PaymentService().create_checkout(str(user.id), user.email)
    except PaymentConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/mock-upgrade")
async def mock_upgrade(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if settings.billing_mode != "mock":
        raise HTTPException(status_code=400, detail="Mock billing is disabled")
    subscription = await _subscription_for_user(db, user.id)
    if subscription is None:
        subscription = Subscription(user_id=user.id, plan=Plan.PREMIUM, status="active")
        db.add(subscription)
    else:
        subscription.plan = Plan.PREMIUM
        subscription.status = "active"
    user.role = UserRole.PREMIUM
    await db.commit()
    return {"message": "Development account upgraded to premium"}


@router.post("/portal")
async def portal(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    subscription = await _subscription_for_user(db, user.id)
    customer_id = subscription.stripe_customer_id if subscription else ""
    try:
        return await PaymentService().create_portal(customer_id or "")
    except (PaymentConfigurationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def _activate_subscription(
    db: AsyncSession,
    user_id: UUID,
    stripe_object: dict[str, Any],
) -> None:
    user = await db.get(User, user_id)
    if user is None:
        raise ValueError("Webhook references an unknown user")
    subscription = await _subscription_for_user(db, user_id)
    if subscription is None:
        subscription = Subscription(user_id=user_id)
        db.add(subscription)
    user.role = UserRole.PREMIUM
    subscription.plan = Plan.PREMIUM
    subscription.status = "active"
    subscription.stripe_customer_id = stripe_object.get("customer")
    subscription.stripe_subscription_id = stripe_object.get("subscription") or stripe_object.get("id")


async def _deactivate_subscription(db: AsyncSession, stripe_subscription_id: str) -> None:
    subscription = await db.scalar(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
    )
    if subscription is None:
        return
    subscription.plan = Plan.FREE
    subscription.status = "canceled"
    subscription.cancel_at_period_end = False
    user = await db.get(User, subscription.user_id)
    if user is not None:
        user.role = UserRole.USER


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    if settings.billing_mode != "stripe":
        return {"received": True, "mode": "mock"}
    try:
        event = PaymentService().construct_event(await request.body(), stripe_signature)
    except (PaymentConfigurationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc

    event_id = str(event.get("id", ""))
    event_type = str(event.get("type", "unknown"))
    if not event_id:
        raise HTTPException(status_code=400, detail="Stripe event has no ID")
    existing = await db.scalar(
        select(PaymentWebhookEvent).where(
            PaymentWebhookEvent.provider_event_id == event_id
        )
    )
    if existing and existing.processed:
        return {"received": True, "type": event_type, "duplicate": True}

    record = existing or PaymentWebhookEvent(
        provider_event_id=event_id,
        event_type=event_type,
        payload_json={"id": event_id, "type": event_type},
    )
    if existing is None:
        db.add(record)

    obj: dict[str, Any] = event["data"]["object"]
    try:
        if event_type == "checkout.session.completed":
            raw_user_id = (obj.get("metadata") or {}).get("user_id")
            if raw_user_id:
                await _activate_subscription(db, UUID(raw_user_id), obj)
        elif event_type in {
            "customer.subscription.deleted",
            "customer.subscription.paused",
        }:
            await _deactivate_subscription(db, str(obj.get("id", "")))
        elif event_type == "customer.subscription.updated":
            subscription = await db.scalar(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == str(obj.get("id", ""))
                )
            )
            if subscription:
                subscription.status = str(obj.get("status", subscription.status))
                subscription.cancel_at_period_end = bool(obj.get("cancel_at_period_end", False))
        elif event_type == "invoice.payment_failed":
            subscription_id = str(obj.get("subscription", ""))
            subscription = await db.scalar(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == subscription_id
                )
            )
            if subscription:
                subscription.status = "past_due"

        record.processed = True
        record.error_message = None
        record.updated_at = datetime.now(UTC)
        await db.commit()
    except Exception as exc:
        record.error_message = str(exc)[:500]
        await db.commit()
        raise HTTPException(status_code=500, detail="Webhook processing failed") from exc
    return {"received": True, "type": event_type, "duplicate": False}
