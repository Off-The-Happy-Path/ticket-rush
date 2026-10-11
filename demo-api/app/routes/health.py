from fastapi import APIRouter

from app.config import settings
from app.models import Health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Health)
async def health() -> Health:
    return Health(oversell_bug=settings.oversell_bug, admin_enabled=settings.admin_enabled)
