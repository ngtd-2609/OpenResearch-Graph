from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

try:
    import stripe
except ImportError:
    stripe = None  # type: ignore[assignment]

from app.core.config import settings

T = TypeVar("T")


class PaymentConfigurationError(RuntimeError):
    """Raised when Stripe mode is enabled without complete configuration."""


class PaymentService:
    def __init__(self) -> None:
        if settings.billing_mode == "stripe":
            missing = [
                name
                for name, value in {
                    "STRIPE_SECRET_KEY": settings.stripe_secret_key,
                    "STRIPE_WEBHOOK_SECRET": settings.stripe_webhook_secret,
                    "STRIPE_PRICE_PREMIUM_MONTHLY": settings.stripe_price_premium_monthly,
                }.items()
                if not value
            ]
            if missing:
                raise PaymentConfigurationError(f"Missing Stripe settings: {', '.join(missing)}")
        if settings.stripe_secret_key and stripe is not None:
            stripe.api_key = settings.stripe_secret_key

    @staticmethod
    async def _run_sync(call: Callable[..., T], **kwargs: Any) -> T:
        """Run the synchronous Stripe SDK outside the event loop."""
        return await asyncio.to_thread(call, **kwargs)

    async def create_checkout(self, user_id: str, email: str) -> dict[str, Any]:
        if settings.billing_mode == "mock":
            return {
                "mode": "mock",
                "checkout_url": f"{settings.frontend_url}/account?mock_upgrade=1",
            }
        if stripe is None:
            raise PaymentConfigurationError("Install stripe to enable BILLING_MODE=stripe")
        session = await self._run_sync(
            stripe.checkout.Session.create,
            mode="subscription",
            customer_email=email,
            line_items=[{"price": settings.stripe_price_premium_monthly, "quantity": 1}],
            success_url=f"{settings.frontend_url}/account?checkout=success",
            cancel_url=f"{settings.frontend_url}/pricing?checkout=cancelled",
            metadata={"user_id": user_id},
            allow_promotion_codes=True,
        )
        if not session.url:
            raise RuntimeError("Stripe did not return a checkout URL")
        return {"mode": "stripe", "checkout_url": session.url}

    async def create_portal(self, customer_id: str) -> dict[str, str]:
        if settings.billing_mode == "mock":
            return {"portal_url": f"{settings.frontend_url}/account"}
        if stripe is None:
            raise PaymentConfigurationError("Install stripe to enable BILLING_MODE=stripe")
        if not customer_id:
            raise ValueError("Stripe customer ID is required")
        session = await self._run_sync(
            stripe.billing_portal.Session.create,
            customer=customer_id,
            return_url=f"{settings.frontend_url}/account",
        )
        if not session.url:
            raise RuntimeError("Stripe did not return a portal URL")
        return {"portal_url": session.url}

    def construct_event(self, body: bytes, signature: str) -> Any:
        if stripe is None:
            raise PaymentConfigurationError("Install stripe to verify webhooks")
        if not signature:
            raise ValueError("Missing Stripe-Signature header")
        return stripe.Webhook.construct_event(body, signature, settings.stripe_webhook_secret)
