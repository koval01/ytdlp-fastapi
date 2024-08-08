"""
Route handler for /v1/video/{video_id}
"""

import asyncio

import yt_dlp
from fastapi import Request, HTTPException, APIRouter, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.error import HTTPError
from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.cookies import CookieConverter
from app.utils.dlp_utils import DLPUtils
from app.utils.url_replacer import URLValidator

router = APIRouter()

yt_dlp_options = {
    'no_warnings': True,
    'noprogress': True,
    'quiet': True,
    'http_headers': {"Cookie": CookieConverter(settings.COOKIES).convert()},
}
if not settings.HLS_MODE:
    yt_dlp_options["format"] = DLPUtils.format_selector

loop = asyncio.get_event_loop()


@router.get(
    "/video/{video_id}",
    summary="Get video information",
    responses={
        200: {"model": YouTubeResponse},
        400: {"model": HTTPError},
        401: {"model": HTTPError}
    },
    tags=["Video"]
)
async def fetch(request: Request, video_id: str, x_secret: str | None = Header(None)) -> JSONResponse:
    """Request handler"""
    if x_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
        try:
            resp = await loop.run_in_executor(None, ydl.extract_info, f"https://www.youtube.com/watch?v={video_id}", False)
            _validator = URLValidator(request)
            return JSONResponse(
                content=jsonable_encoder(_validator.replace_urls(resp).model_dump())
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
