from fastapi import APIRouter

from . import video, playback

router = APIRouter(prefix="/v1")

router.include_router(video.router)
router.include_router(playback.router)
