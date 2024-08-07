from fastapi import APIRouter

from . import hls, segment

router = APIRouter(prefix="/manifest")

router.include_router(hls.router)
router.include_router(segment.router)
