from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graphs", tags=["graphs"])


@router.get("/citations")
async def citation_graph(limit: int = Query(80, ge=5, le=300), db: AsyncSession = Depends(get_db)) -> dict:
    return await GraphService().citation_graph(db, limit)
