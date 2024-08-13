"""
Route handler for /v1/video/{video_id}
"""

from typing import Annotated, Dict, Any

import yt_dlp
import asyncio
import logging
from fastapi import Request, HTTPException, APIRouter, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.error import HTTPError
from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.cookies import CookieConverter
from app.utils.url_replacer import URLValidator

router = APIRouter()
logger = logging.getLogger("video_fetch")


async def extract_info_async(ydl: yt_dlp.YoutubeDL, video_url: str) -> Dict[str, Any]:
    """
    Asynchronously extract information from a YouTube video URL using yt_dlp.

    Args:
        ydl (yt_dlp.YoutubeDL): An instance of the yt_dlp.YoutubeDL class.
        video_url (str): The URL of the YouTube video.

    Returns:
        Dict[str, Any]: A dictionary containing the extracted video information.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, ydl.extract_info, video_url, False)


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
async def fetch(request: Request, video_id: str, x_secret: Annotated[str | None, Header()] = None) -> JSONResponse:
    """Request handler"""
    if x_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    yt_dlp_options = {
        'no_warnings': True,
        'noprogress': True,
        'quiet': True,
        'getcomments': True,
        'extractor_args': {'youtube': {'max_comments': ['20']}},
        'http_headers': {"Cookie": CookieConverter(settings.COOKIES).convert()},
    }
    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
        try:
            resp = await extract_info_async(ydl, f"https://www.youtube.com/watch?v={video_id}")
            _validator = URLValidator(request)
            return JSONResponse(
                content=jsonable_encoder(_validator.replace_urls(resp).model_dump())
            )
        except Exception as e:
            logger.warning(f"Error fetch video with ID:{video_id}. Error details: {e}")
            raise HTTPException(status_code=500, detail="Internal application error")
