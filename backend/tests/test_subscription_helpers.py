from typing import Any
from uuid import uuid4

import pytest

from app.api.v1.subscriptions import _activate_subscription, _deactivate_subscription
from app.models.entities import Plan, Subscription, User, UserRole
from app.core.security import hash_password


class FakeDb:
    def __init__(self, *, scalar: Any = None, user: User | None = None) -> None:
        self.scalar_value = scalar
        self.user = user
        self.added: list[Any] = []

    async def scalar(self, _statement: Any) -> Any:
        return self.scalar_value

    async def get(self, model: type, _key: Any) -> Any:
        return self.user if model is User else None

    def add(self, item: Any) -> None:
        self.added.append(item)


def make_user() -> User:
    return User(
        id=uuid4(), email="pay@example.com", username="pay", full_name="Pay",
        password_hash=hash_password("Student123!"), role=UserRole.USER,
        is_active=True, is_verified=True,
    )


@pytest.mark.asyncio
async def test_activate_subscription_creates_missing_record() -> None:
    user = make_user()
    db = FakeDb(user=user)
    await _activate_subscription(
        db, user.id, {"customer": "cus_1", "subscription": "sub_1"}  # type: ignore[arg-type]
    )
    assert user.role == UserRole.PREMIUM
    assert len(db.added) == 1
    subscription = db.added[0]
    assert subscription.plan == Plan.PREMIUM
    assert subscription.stripe_subscription_id == "sub_1"


@pytest.mark.asyncio
async def test_deactivate_subscription_downgrades_user() -> None:
    user = make_user()
    user.role = UserRole.PREMIUM
    subscription = Subscription(
        id=uuid4(), user_id=user.id, plan=Plan.PREMIUM, status="active",
        stripe_subscription_id="sub_1", cancel_at_period_end=True,
    )
    db = FakeDb(scalar=subscription, user=user)
    await _deactivate_subscription(db, "sub_1")  # type: ignore[arg-type]
    assert subscription.plan == Plan.FREE
    assert subscription.status == "canceled"
    assert user.role == UserRole.USER
