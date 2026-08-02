from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models.entities import User, UserRole
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/integrations")
async def integrations(
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return redacted configuration and health status for external services."""
    return await IntegrationService().statuses(db)
