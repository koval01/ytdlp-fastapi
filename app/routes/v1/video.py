"""
Route handler for /v1/video/{video_id}
"""

from typing import Annotated

import yt_dlp
from fastapi import Request, HTTPException, APIRouter, Header
from fastapi.responses import JSONResponse

from app.models.error import HTTPError
from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.cookies import CookieConverter
from app.utils.dlp_utils import DLPUtils
from app.utils.url_replacer import URLValidator

router = APIRouter()


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
def fetch(request: Request, video_id: str, x_secret: Annotated[str | None, Header()] = None) -> JSONResponse:
    """Request handler"""
    if x_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    yt_dlp_options = {
        'quiet': True,
        'no-warnings': True,
        # since downloading cookies from a file, and even more so from a browser,
        # is problematic on hosting, so the following authorization method is used
        'http_headers': {"Cookie": CookieConverter(settings.COOKIES).convert()},
    }
    if not settings.HLS_MODE:
        yt_dlp_options["format"] = DLPUtils.format_selector

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
        try:
            resp = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )
            return JSONResponse(URLValidator(request).replace_urls(resp))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
