from fastapi import APIRouter, Depends
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.entities import Paper

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
async def trends(db: AsyncSession = Depends(get_db)) -> dict:
    rows = (await db.execute(
        select(Paper.publication_year, func.count(Paper.id), func.sum(Paper.cited_by_count))
        .where(Paper.publication_year.is_not(None))
        .group_by(Paper.publication_year)
        .order_by(Paper.publication_year)
    )).all()
    return {"series": [{"year": year, "papers": count, "citations": citations or 0} for year, count, citations in rows]}


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db)) -> dict:
    count, citations, open_access = (await db.execute(select(
        func.count(Paper.id), func.sum(Paper.cited_by_count), func.sum(cast(Paper.is_open_access, Integer))
    ))).one()
    return {"papers": count, "citations": citations or 0, "open_access_papers": open_access or 0}
