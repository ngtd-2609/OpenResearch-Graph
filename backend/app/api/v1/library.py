from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import current_user
from app.db.session import get_db
from app.models.entities import LibraryItem, Paper, User, UserPaperInteraction
from app.schemas.common import PaperPublic

router = APIRouter(prefix="/library", tags=["library"])


class SavePaperRequest(BaseModel):
    paper_id: UUID
    collection_name: str = Field(default="Saved", min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=5_000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class UpdateLibraryItemRequest(BaseModel):
    collection_name: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=5_000)
    tags: list[str] | None = Field(default=None, max_length=20)


def _serialize(item: LibraryItem) -> dict[str, object]:
    return {
        "id": str(item.id),
        "paper": PaperPublic.model_validate(item.paper).model_dump(mode="json"),
        "collection_name": item.collection_name,
        "notes": item.notes,
        "tags": item.tags,
    }


@router.get("")
async def get_library(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    items = list(
        (
            await db.scalars(
                select(LibraryItem)
                .options(selectinload(LibraryItem.paper))
                .where(LibraryItem.user_id == user.id)
                .order_by(LibraryItem.created_at.desc())
            )
        ).all()
    )
    return [_serialize(item) for item in items]


@router.post("", status_code=201)
async def save_paper(
    payload: SavePaperRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    if await db.get(Paper, payload.paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    existing = await db.scalar(
        select(LibraryItem).where(
            LibraryItem.user_id == user.id,
            LibraryItem.paper_id == payload.paper_id,
        )
    )
    if existing:
        return {"id": existing.id, "message": "Already saved"}
    item = LibraryItem(
        user_id=user.id,
        paper_id=payload.paper_id,
        collection_name=payload.collection_name,
        notes=payload.notes,
        tags=list(dict.fromkeys(payload.tags)),
        created_at=datetime.now(UTC),
    )
    db.add(item)
    db.add(
        UserPaperInteraction(
            user_id=user.id,
            paper_id=payload.paper_id,
            interaction_type="save",
            interaction_value=1.0,
        )
    )
    await db.commit()
    return {"id": item.id, "message": "Saved"}


@router.patch("/{paper_id}")
async def update_item(
    paper_id: UUID,
    payload: UpdateLibraryItemRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    item = await db.scalar(
        select(LibraryItem).where(
            LibraryItem.user_id == user.id,
            LibraryItem.paper_id == paper_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Library item not found")
    if payload.collection_name is not None:
        item.collection_name = payload.collection_name
    if payload.notes is not None:
        item.notes = payload.notes
    if payload.tags is not None:
        item.tags = list(dict.fromkeys(payload.tags))
    await db.commit()
    return {"message": "Library item updated"}


@router.delete("/{paper_id}")
async def remove_paper(
    paper_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    item = await db.scalar(
        select(LibraryItem).where(
            LibraryItem.user_id == user.id,
            LibraryItem.paper_id == paper_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Library item not found")
    await db.delete(item)
    db.add(
        UserPaperInteraction(
            user_id=user.id,
            paper_id=paper_id,
            interaction_type="unsave",
            interaction_value=1.0,
        )
    )
    await db.commit()
    return {"message": "Removed"}
