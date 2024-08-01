"""
Route handler for /v1/video/{video_id}
"""
from __future__ import annotations

import re
from typing import Annotated, Optional

import yt_dlp
from fastapi import Request, HTTPException, Header
from fastapi.responses import JSONResponse

from models.error import HTTPError
from routes.v1.router import router

from utils.config import settings
from utils.url_replacer import URLReplacer


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
def fetch(request: Request, video_id: str, x_secret: Annotated[Optional[str], Header()]) -> JSONResponse:
    """Request handler"""
    if x_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with yt_dlp.YoutubeDL({}) as ydl:
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
