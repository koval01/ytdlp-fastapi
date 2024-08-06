"""
Route handler for /v1/video/{video_id}
"""

import re
from typing import Annotated

import yt_dlp
from fastapi import Request, HTTPException, APIRouter, Header
from fastapi.responses import JSONResponse

from app.models.error import HTTPError
from app.utils.config import settings
from app.utils.url_replacer import URLReplacer

router = APIRouter()


def format_selector(ctx):
    """Select the best video and the best audio"""

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


@router.get(
    "/video/{video_id}",
    summary="Get video information",
    responses={
        200: {"model": HTTPError},
        400: {"model": HTTPError},
        401: {"model": HTTPError}
    },
    tags=["Video"]
)
def fetch(request: Request, video_id: str, x_secret: Annotated[str | None, Header()] = None) -> JSONResponse:
    """Request handler"""
    if x_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with yt_dlp.YoutubeDL({
        'cookies': settings.COOKIES,
        'format': format_selector
    }) as ydl:
        try:
            resp = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )
            return JSONResponse(URLReplacer(request).replace_urls(resp))
        except Exception as e:
            error = re.search(r"\[.*?] (.+): (.+)", str(e))
            raise HTTPException(
                status_code=400, detail={"error": error.group(2), "id": error.group(1)})
