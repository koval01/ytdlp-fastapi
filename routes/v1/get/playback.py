"""
Route handler for /v1/playback/{playback_token}
"""

from cryptography.fernet import InvalidToken
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from models.error import HTTPError
from models.playback import Playback

from routes.v1.router import router

from utils.crypto import Cryptography
from utils.range_request import RangeRequestHandler


@router.get(
    "/playback/{playback_token}",
    summary="Get media stream",
    responses={
        200: {"content": {"video/mp4": {}}},
        400: {"model": HTTPError},
        401: {"model": HTTPError},
        500: {"model": HTTPError}
    },
    tags=["Video"]
)
async def playback(request: Request, playback_token: str) -> StreamingResponse:
    """Request handler"""
    try:
        data = Cryptography().decrypt_json(playback_token)
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid media token")

    try:
        data = Playback(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if data.client_host != request.client.host:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await RangeRequestHandler(
        f"https://rr{data.host}.googlevideo.com/videoplayback?{data.query}"
    ).range_requests_response(request, content_type="video/mp4")
