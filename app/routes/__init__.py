from fastapi import APIRouter

from app.utils.config import settings
from . import templates, healthz, v1

router = APIRouter()

if not bool(settings.DISABLE_DEMO):
    router.include_router(templates.router)

router.include_router(healthz.router)
router.include_router(v1.router)
