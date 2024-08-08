import re
from typing import AsyncIterable

from aiohttp import ClientSession, ClientResponseError
from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from yarl import URL

from app.models.crypto import CryptoObject
from app.models.error import HTTPError
from app.utils.crypto import Cryptography

router = APIRouter()

SEGMENT_TOKEN_PATTERN = re.compile(r'\.[a-zA-Z0-9]+$')
cryptography = Cryptography()
session = ClientSession()


@router.get(
    "/segment/{segment_token}",
    summary="Get video segment (HLS stream)",
    responses={
        200: {"content": {"application/octet-stream": {}}},
        400: {"model": HTTPError},
        500: {"model": HTTPError},
    },
    tags=["Util"]
)
async def segment(request: Request, segment_token: str) -> StreamingResponse:
    """Request handler"""
    try:
        token = SEGMENT_TOKEN_PATTERN.sub('', segment_token)
        data = cryptography.decrypt_json(token)
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if str(data.client_host) != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    async def stream_video() -> AsyncIterable[bytes]:
        try:
            async with session.get(URL(str(data.url), encoded=True)) as resp:
                async for chunk in resp.content.iter_chunked(1024):
                    yield chunk
        except ClientResponseError as _e:
            raise HTTPException(status_code=500, detail=str(_e))

    return StreamingResponse(content=stream_video(), media_type="application/octet-stream")
