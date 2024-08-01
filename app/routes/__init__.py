from fastapi import APIRouter

from . import healthz, v1

router = APIRouter()

router.include_router(healthz.router)
router.include_router(v1.router)
