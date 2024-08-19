"""
Route handler for /v1/video/{video_id}
"""

import asyncio
from typing import Annotated, Dict, Any

import yt_dlp
from fastapi import Request, HTTPException, APIRouter, Header
from fastapi.encoders import jsonable_encoder
from fastapi.logger import logger
from fastapi.responses import JSONResponse

from app.models.error import HTTPError
from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.dlp_utils import DLPUtils
from app.utils.cookies import CookieConverter
from app.utils.url_replacer import URLValidator
from app.utils.turnstile import TurnstileValidator

router = APIRouter()


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
    logger.info(f"Client {request.client.host} requested video {video_id} with X-Secret {x_secret}")
    if not x_secret:
        raise HTTPException(status_code=401)

    if not DLPUtils.validate_youtube_video_id(video_id):
        logger.warning(f"Video id {video_id} is invalid")
        raise HTTPException(status_code=400)

    if bool(settings.DISABLE_TURNSTILE):
        if x_secret != settings.SECRET_KEY:
            logger.warning(f"x_secret != settings.SECRET_KEY for {request.client.host}")
            raise HTTPException(status_code=401)
    else:
        turnstile_status = await TurnstileValidator().validate(x_secret)
        if not turnstile_status:
            logger.warning(f"Not valid turnstile key for {request.client.host}")
            raise HTTPException(status_code=401)

    yt_dlp_options = {
        'no_warnings': True,
        'noprogress': True,
        'quiet': True,
        'getcomments': True,
        'extractor_args': {
            'youtube': {
                'comment_sort': ['top'],
                'max_comments': ['100', 'all', '0', '0'],
            }
        },
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
