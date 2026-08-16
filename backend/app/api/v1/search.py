from uuid import NAMESPACE_URL, uuid5

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import optional_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Paper, User, UserRole
from app.schemas.common import PaginatedPapers
from app.services.openalex_service import OpenAlexService
from app.services.paper_search_service import PaperSearchFilters, PaperSearchService
from app.services.rate_limit_service import RateLimitService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/papers", response_model=PaginatedPapers)
async def search_papers(
    request: Request,
    response: Response,
    query: str = Query(min_length=2, max_length=300),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    from_year: int | None = Query(None, ge=1900),
    to_year: int | None = Query(None, ge=1900),
    open_access: bool | None = None,
    author: str | None = Query(None, max_length=160),
    institution: str | None = Query(None, max_length=200),
    topic: str | None = Query(None, max_length=160),
    paper_type: str | None = Query(None, max_length=80),
    user: User | None = Depends(optional_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPapers:
    if from_year and to_year and from_year > to_year:
        raise HTTPException(status_code=422, detail="from_year must be less than or equal to to_year")

    identity = str(user.id) if user else (request.client.host if request.client else "anonymous")
    limit = (
        settings.premium_searches_per_hour
        if user and user.role in {UserRole.PREMIUM, UserRole.ADMIN}
        else settings.free_searches_per_hour
    )
    allowed, remaining = await RateLimitService().allow(f"search:{identity}", limit)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    if not allowed:
        raise HTTPException(status_code=429, detail="Search rate limit exceeded")

    total, papers = await PaperSearchService().search(
        db,
        query=query,
        filters=PaperSearchFilters(
            from_year=from_year,
            to_year=to_year,
            open_access=open_access,
            author=author,
            institution=institution,
            topic=topic,
            paper_type=paper_type,
        ),
        page=page,
        per_page=per_page,
    )
    if not papers and OpenAlexService().configured:
        remote = await OpenAlexService().search_works(
            query,
            page,
            per_page,
            from_year=from_year,
            to_year=to_year,
            open_access=open_access,
        )
        papers = []
        for item in remote.get("results", []):
            normalized = OpenAlexService.normalize_work(item)
            normalized["id"] = uuid5(
                NAMESPACE_URL,
                normalized.get("openalex_id") or normalized["title"],
            )
            # Persist / merge paper into database so Detail & Save routes work seamlessly
            paper_obj = Paper(**normalized)
            if hasattr(db, "merge"):
                try:
                    merged = await db.merge(paper_obj)
                    if merged is not None:
                        paper_obj = merged
                except Exception:
                    pass
            papers.append(paper_obj)
        if hasattr(db, "commit"):
            try:
                await db.commit()
            except Exception:
                if hasattr(db, "rollback"):
                    await db.rollback()
        total = int(remote.get("meta", {}).get("count", len(papers)))
    return PaginatedPapers(
        query=query,
        total=total,
        page=page,
        per_page=per_page,
        items=papers,
    )
