"""
Route handler for /v1/manifest/segment/{segment_token}
"""
import re

from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.models.error import HTTPError
from app.models.crypto import CryptoObject
from app.utils.crypto import Cryptography
from aiohttp import ClientSession
from yarl import URL
from io import BytesIO

router = APIRouter()


@router.get(
    "/segment/{segment_token}",
    summary="Get video segment (HLS stream)",
    responses={
        200: {"content": {
            "application/octet-stream": {}
        }},
        400: {"model": HTTPError},
        500: {"model": HTTPError}
    },
    tags=["Util"]
)
async def segment(request: Request, segment_token: str) -> StreamingResponse:
    """Request handler"""
    try:
        data = Cryptography().decrypt_json(re.sub(r'\.[a-zA-Z0-9]+$', '', segment_token))
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if str(data.client_host) != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    async with ClientSession() as session:
        try:
            async with session.get(URL(str(data.url), encoded=True)) as response:
                response.raise_for_status()
                segment_data = BytesIO(await response.read())
                return StreamingResponse(
                    segment_data,
                    media_type=response.headers.get('Content-Type', 'application/octet-stream')
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
