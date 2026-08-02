from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api import dependencies
from app.core.security import create_access_token
from app.models.entities import User, UserRole


class FakeDb:
    def __init__(self, item: Any = None) -> None:
        self.item = item

    async def get(self, _model: type, _key: object) -> Any:
        return self.item


def make_user(*, active: bool = True, role: UserRole = UserRole.USER) -> User:
    return User(
        id=uuid4(),
        email="user@example.com",
        username="user",
        password_hash="hash",
        role=role,
        is_active=active,
    )


@pytest.mark.asyncio
async def test_optional_user_accepts_anonymous_request() -> None:
    assert await dependencies.optional_user(None, FakeDb()) is None  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_current_user_requires_bearer_token() -> None:
    with pytest.raises(HTTPException) as exc:
        await dependencies.current_user(None, FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_resolve_user_accepts_valid_access_token() -> None:
    user = make_user()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(str(user.id), role=user.role.value),
    )
    resolved = await dependencies.current_user(credentials, FakeDb(user))  # type: ignore[arg-type]
    assert resolved.id == user.id


@pytest.mark.asyncio
async def test_resolve_user_rejects_invalid_and_inactive_accounts() -> None:
    invalid = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-jwt")
    with pytest.raises(HTTPException) as exc:
        await dependencies.current_user(invalid, FakeDb())  # type: ignore[arg-type]
    assert exc.value.status_code == 401

    inactive = make_user(active=False)
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(str(inactive.id), role=inactive.role.value),
    )
    with pytest.raises(HTTPException) as exc:
        await dependencies.current_user(credentials, FakeDb(inactive))  # type: ignore[arg-type]
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_require_role_enforces_authorization() -> None:
    dependency = dependencies.require_role(UserRole.ADMIN)
    with pytest.raises(HTTPException) as exc:
        await dependency(make_user(role=UserRole.USER))
    assert exc.value.status_code == 403
    admin = make_user(role=UserRole.ADMIN)
    assert await dependency(admin) is admin
