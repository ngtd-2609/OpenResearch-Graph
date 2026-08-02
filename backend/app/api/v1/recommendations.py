from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user
from app.db.session import get_db
from app.models.entities import Paper, User, UserPaperInteraction
from app.schemas.common import PaperPublic
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class FeedbackRequest(BaseModel):
    interaction_type: Literal["view", "click", "save", "download", "like", "dislike", "dismiss", "chat"]
    value: float = Field(default=1.0, ge=-10, le=10)


@router.get("")
async def recommendations(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    items = await RecommendationService().recommend(db, user.id)
    return [
        {
            "paper": PaperPublic.model_validate(item.paper).model_dump(mode="json"),
            "score": item.score,
            "explanation": item.explanation,
            "components": item.components,
        }
        for item in items
    ]


@router.post("/{paper_id}/feedback")
async def feedback(
    paper_id: UUID,
    payload: FeedbackRequest,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if await db.get(Paper, paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    db.add(
        UserPaperInteraction(
            user_id=user.id,
            paper_id=paper_id,
            interaction_type=payload.interaction_type,
            interaction_value=payload.value,
        )
    )
    await db.commit()
    return {"message": "Feedback recorded"}
