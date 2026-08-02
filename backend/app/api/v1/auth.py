from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_action_token,
    create_refresh_token,
    hash_password,
    hash_token,
    password_needs_rehash,
    verify_password,
)
from app.db.session import get_db
from app.models.entities import ActionToken, RefreshToken, Subscription, User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.common import UserPublic
from app.services.email_service import EmailService
from app.services.rate_limit_service import RateLimitService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserPublic, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
    normalized_email = payload.email.lower()
    exists = await db.scalar(
        select(User.id).where(
            or_(User.email == normalized_email, User.username == payload.username)
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="Email or username already exists")
    user = User(
        email=normalized_email,
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.flush()
    db.add(Subscription(user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    identity = f"login:{request.client.host if request.client else 'unknown'}:{payload.email.lower()}"
    allowed, _ = await RateLimitService().allow(
        identity,
        settings.login_attempts_per_15_minutes,
        window_seconds=900,
    )
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many login attempts")

    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)

    raw_refresh, token_hash, expires_at = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            family_id=uuid4(),
            expires_at=expires_at,
            device_info=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    )
    user.last_login_at = datetime.now(UTC)
    await db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=raw_refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    token_hash = hash_token(payload.refresh_token)
    stored = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if stored is None or stored.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if stored.revoked_at:
        if stored.family_id:
            await db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.family_id == stored.family_id,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=datetime.now(UTC))
            )
            await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")

    user = await db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    stored.revoked_at = datetime.now(UTC)
    raw_refresh, new_hash, expires_at = create_refresh_token()
    stored.replaced_by_hash = new_hash
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            family_id=stored.family_id or uuid4(),
            expires_at=expires_at,
        )
    )
    await db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=raw_refresh,
    )


@router.post("/logout")
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    stored = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_token(payload.refresh_token)
        )
    )
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(UTC)
        await db.commit()
    return {"message": "Logged out"}


@router.post("/logout-all")
async def logout_all(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    await db.commit()
    return {"message": "All sessions have been revoked"}


@router.get("/me", response_model=UserPublic)
async def me(user: User = Depends(current_user)) -> User:
    return user


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if user:
        raw, token_hash, expires_at = create_action_token(timedelta(minutes=30))
        db.add(
            ActionToken(
                user_id=user.id,
                token_hash=token_hash,
                purpose="reset-password",
                expires_at=expires_at,
            )
        )
        await db.commit()
        await EmailService().send_action_link(
            user.email,
            "Reset password",
            f"{settings.frontend_url}/reset-password?token={raw}",
        )
    return {"message": "If the account exists, a reset link has been generated."}


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    token = await db.scalar(
        select(ActionToken).where(
            ActionToken.token_hash == hash_token(payload.token),
            ActionToken.purpose == "reset-password",
        )
    )
    if token is None or token.used_at or token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = await db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(payload.new_password)
    token.used_at = datetime.now(UTC)
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    await db.commit()
    return {"message": "Password changed"}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    await db.commit()
    return {"message": "Password changed; other sessions were revoked"}


@router.post("/request-verification")
async def request_verification(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    raw, token_hash, expires_at = create_action_token(timedelta(hours=24))
    db.add(
        ActionToken(
            user_id=user.id,
            token_hash=token_hash,
            purpose="verify-email",
            expires_at=expires_at,
        )
    )
    await db.commit()
    await EmailService().send_action_link(
        user.email,
        "Verify email",
        f"{settings.frontend_url}/verify-email?token={raw}",
    )
    return {"message": "Verification link generated"}


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    token = await db.scalar(
        select(ActionToken).where(
            ActionToken.token_hash == hash_token(payload.token),
            ActionToken.purpose == "verify-email",
        )
    )
    if token is None or token.used_at or token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    user = await db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    token.used_at = datetime.now(UTC)
    await db.commit()
    return {"message": "Email verified"}
