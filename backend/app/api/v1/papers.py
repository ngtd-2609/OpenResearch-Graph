from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.entities import Paper
from app.schemas.common import PaperPublic

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/{paper_id}", response_model=PaperPublic)
async def paper_detail(paper_id: UUID, db: AsyncSession = Depends(get_db)) -> Paper:
    paper = await db.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.get("/{paper_id}/related", response_model=list[PaperPublic])
async def related_papers(paper_id: UUID, db: AsyncSession = Depends(get_db)) -> list[Paper]:
    paper = await db.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    words = [word for word in paper.title.split() if len(word) > 4][:4]
    condition = Paper.id != paper_id
    query = select(Paper).where(condition)
    if words:
        from sqlalchemy import or_

        query = query.where(or_(*(Paper.title.ilike(f"%{word}%") for word in words)))
    return list((await db.scalars(query.order_by(Paper.cited_by_count.desc()).limit(10))).all())
