import re

from aiohttp import ClientSession
from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.logger import logger
from fastapi.responses import Response
from pydantic import ValidationError
from yarl import URL

from app.models.crypto import CryptoObject
from app.models.error import HTTPError
from app.utils.crypto import Cryptography
from app.utils.hls import HLSReplacer

router = APIRouter()

MANIFEST_TOKEN_PATTERN = re.compile(r'\.[a-zA-Z0-9]+$')
cryptography = Cryptography()


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
        token = MANIFEST_TOKEN_PATTERN.sub('', manifest_token)
        data = cryptography.decrypt_json(token)
    except InvalidToken as e:
        logger.warning(f"Error validation manifest token. Details: {e}")
        raise HTTPException(status_code=400)

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if str(data.client_host) != request.client.host:
        logger.warning(f"Client IP is invalid. C:{str(data.client_host)} F:{request.client.host}")
        raise HTTPException(status_code=400)

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
