"""
Route handler for /v1/manifest/hls/{manifest_token}
"""

import re

from aiohttp import ClientSession
from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError
from yarl import URL

from app.models.crypto import CryptoObject
from app.models.error import HTTPError
from app.utils.crypto import Cryptography
from app.utils.hls import HLSReplacer

router = APIRouter()


@router.get(
    "/hls/{manifest_token}",
    summary="Get HLS manifest of video",
    responses={
        200: {"content": {
            "application/vnd.apple.mpegurl": {}
        }},
        400: {"model": HTTPError},
        500: {"model": HTTPError}
    },
    tags=["Util"]
)
async def hls_manifest(request: Request, manifest_token: str) -> Response:
    """Request handler"""
    try:
        data = Cryptography().decrypt_json(re.sub(r'\.[a-zA-Z0-9]+$', '', manifest_token))
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid manifest token")

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if str(data.client_host) != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid manifest token")

    async with ClientSession() as session:
        try:
            async with session.get(URL(str(data.url), encoded=True)) as response:
                response.raise_for_status()
                resp = await response.text()
                return Response(
                    HLSReplacer.replace_manifest_links(resp, request),
                    media_type=response.headers.get('Content-Type', 'application/vnd.apple.mpegurl')
                )
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))
