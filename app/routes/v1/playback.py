"""
Route handler for /v1/playback/{playback_token}
"""

import re

from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.models.error import HTTPError
from app.models.playback import Playback
from app.utils.crypto import Cryptography
from app.utils.range_request import RangeRequestHandler

router = APIRouter()


@router.get(
    "/playback/{playback_token}",
    summary="Get media stream",
    responses={
        200: {"content": {
            "video/mp4": {}, "audio/mp4": {},
            "video/webm": {}, "audio/webm": {}
        }},
        400: {"model": HTTPError},
        500: {"model": HTTPError}
    },
    tags=["Video"]
)
async def playback(request: Request, playback_token: str) -> StreamingResponse:
    """Request handler"""
    try:
        data = Cryptography().decrypt_json(re.sub(r'\.[a-zA-Z0-9]+$', '', playback_token))
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid media token")

    try:
        data = Playback(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if data.client_host != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid media token")

    try:
        return await RangeRequestHandler(
            f"https://rr{data.host}.googlevideo.com/videoplayback?{data.query}"
        ).range_requests_response(request)
    except HTTPException as e:
        raise e
