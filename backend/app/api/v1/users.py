from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.common import UserPublic

router = APIRouter(prefix="/users", tags=["users"])

class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=160)

@router.get("/me", response_model=UserPublic)
async def get_profile(user: User = Depends(current_user)) -> User:
    return user

@router.patch("/me", response_model=UserPublic)
async def update_profile(payload: UpdateProfileRequest, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> User:
    user.full_name = payload.full_name
    await db.commit(); await db.refresh(user)
    return user
