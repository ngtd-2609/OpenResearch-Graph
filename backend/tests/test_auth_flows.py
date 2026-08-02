from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1 import auth
from app.core.security import create_refresh_token, hash_password
from app.models.entities import ActionToken, RefreshToken, User, UserRole
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)


class FakeSession:
    def __init__(
        self,
        *,
        scalars: Iterable[Any] = (),
        objects: dict[tuple[type, UUID], Any] | None = None,
    ) -> None:
        self.scalars = list(scalars)
        self.objects = objects or {}
        self.added: list[Any] = []
        self.execute_count = 0
        self.commit_count = 0

    async def scalar(self, _statement: Any) -> Any:
        return self.scalars.pop(0) if self.scalars else None

    async def get(self, model: type, key: UUID) -> Any:
        return self.objects.get((model, key))

    def add(self, item: Any) -> None:
        self.added.append(item)

    async def flush(self) -> None:
        for item in self.added:
            if hasattr(item, "id") and getattr(item, "id", None) is None:
                item.id = uuid4()

    async def execute(self, _statement: Any) -> None:
        self.execute_count += 1

    async def commit(self) -> None:
        self.commit_count += 1

    async def refresh(self, _item: Any) -> None:
        return None


def request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": [(b"user-agent", b"pytest")],
            "client": ("127.0.0.1", 1234),
            "server": ("test", 80),
            "scheme": "http",
            "query_string": b"",
        }
    )


def user(*, active: bool = True, password: str = "Student123!") -> User:
    return User(
        id=uuid4(),
        email="student@example.com",
        username="student",
        full_name="Student",
        password_hash=hash_password(password),
        role=UserRole.USER,
        is_active=active,
        is_verified=False,
    )


@pytest.mark.asyncio
async def test_register_creates_user_and_free_subscription() -> None:
    db = FakeSession(scalars=[None])
    created = await auth.register(
        RegisterRequest(
            email="Student@Example.com",
            username="student",
            full_name="Student",
            password="Student123!",
        ),
        db,  # type: ignore[arg-type]
    )
    assert created.email == "student@example.com"
    assert len(db.added) == 2
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_register_rejects_duplicate_identity() -> None:
    db = FakeSession(scalars=[uuid4()])
    with pytest.raises(HTTPException) as exc:
        await auth.register(
            RegisterRequest(email="student@example.com", username="student", password="Student123!"),
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_login_creates_refresh_session(monkeypatch: pytest.MonkeyPatch) -> None:
    account = user()
    db = FakeSession(scalars=[account])

    async def allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 9

    monkeypatch.setattr(auth.RateLimitService, "allow", allow)
    response = await auth.login(
        LoginRequest(email=account.email, password="Student123!"),
        request(),
        db,  # type: ignore[arg-type]
    )
    assert response.access_token
    assert response.refresh_token
    assert any(isinstance(item, RefreshToken) for item in db.added)
    assert account.last_login_at is not None


@pytest.mark.asyncio
async def test_login_rejects_inactive_account(monkeypatch: pytest.MonkeyPatch) -> None:
    account = user(active=False)
    db = FakeSession(scalars=[account])

    async def allow(*_args: Any, **_kwargs: Any) -> tuple[bool, int]:
        return True, 9

    monkeypatch.setattr(auth.RateLimitService, "allow", allow)
    with pytest.raises(HTTPException) as exc:
        await auth.login(
            LoginRequest(email=account.email, password="Student123!"),
            request(),
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_refresh_rotates_valid_token() -> None:
    account = user()
    raw, token_hash, expires_at = create_refresh_token()
    stored = RefreshToken(
        id=uuid4(),
        user_id=account.id,
        token_hash=token_hash,
        family_id=uuid4(),
        expires_at=expires_at,
        revoked_at=None,
    )
    db = FakeSession(scalars=[stored], objects={(User, account.id): account})
    response = await auth.refresh(RefreshRequest(refresh_token=raw), db)  # type: ignore[arg-type]
    assert response.refresh_token != raw
    assert stored.revoked_at is not None
    assert stored.replaced_by_hash
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_refresh_reuse_revokes_token_family() -> None:
    raw, token_hash, expires_at = create_refresh_token()
    stored = RefreshToken(
        id=uuid4(),
        user_id=uuid4(),
        token_hash=token_hash,
        family_id=uuid4(),
        expires_at=expires_at,
        revoked_at=datetime.now(UTC),
    )
    db = FakeSession(scalars=[stored])
    with pytest.raises(HTTPException) as exc:
        await auth.refresh(RefreshRequest(refresh_token=raw), db)  # type: ignore[arg-type]
    assert exc.value.status_code == 401
    assert db.execute_count == 1
    assert db.commit_count == 1


@pytest.mark.asyncio
async def test_forgot_password_is_non_enumerating(monkeypatch: pytest.MonkeyPatch) -> None:
    account = user()
    db = FakeSession(scalars=[account])
    sent: list[tuple[str, str, str]] = []

    async def send(_self: Any, email: str, subject: str, link: str) -> None:
        sent.append((email, subject, link))

    monkeypatch.setattr(auth.EmailService, "send_action_link", send)
    response = await auth.forgot_password(
        ForgotPasswordRequest(email=account.email),
        db,  # type: ignore[arg-type]
    )
    assert response["message"].startswith("If the account exists")
    assert len(sent) == 1
    assert any(isinstance(item, ActionToken) for item in db.added)


@pytest.mark.asyncio
async def test_reset_password_consumes_token_and_revokes_sessions() -> None:
    account = user()
    token = ActionToken(
        id=uuid4(),
        user_id=account.id,
        token_hash="hash",
        purpose="reset-password",
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
        used_at=None,
    )
    db = FakeSession(scalars=[token], objects={(User, account.id): account})
    response = await auth.reset_password(
        ResetPasswordRequest(token="raw", new_password="NewStudent123!"),
        db,  # type: ignore[arg-type]
    )
    assert response["message"] == "Password changed"
    assert token.used_at is not None
    assert db.execute_count == 1


@pytest.mark.asyncio
async def test_change_password_checks_current_password() -> None:
    account = user()
    db = FakeSession()
    with pytest.raises(HTTPException) as exc:
        await auth.change_password(
            ChangePasswordRequest(current_password="wrong", new_password="NewStudent123!"),
            account,
            db,  # type: ignore[arg-type]
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_verify_email_consumes_action_token() -> None:
    account = user()
    token = ActionToken(
        id=uuid4(),
        user_id=account.id,
        token_hash="hash",
        purpose="verify-email",
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
        used_at=None,
    )
    db = FakeSession(scalars=[token], objects={(User, account.id): account})
    response = await auth.verify_email(
        VerifyEmailRequest(token="raw"),
        db,  # type: ignore[arg-type]
    )
    assert response["message"] == "Email verified"
    assert account.is_verified is True
    assert token.used_at is not None
