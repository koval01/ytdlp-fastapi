"""
Route handler for /v1/manifest/segment/{segment_token}
"""

import re
from io import BytesIO

from aiohttp import ClientSession, ClientResponseError
from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
from yarl import URL

from app.models.crypto import CryptoObject
from app.models.error import HTTPError
from app.utils.crypto import Cryptography

router = APIRouter()


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), retry=retry_if_exception_type(ClientResponseError))
async def fetch_segment_data(url: str) -> BytesIO:
    async with ClientSession() as session:
        async with session.get(URL(url, encoded=True)) as response:
            response.raise_for_status()
            return BytesIO(await response.read())


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
        data = Cryptography().decrypt_json(re.sub(r'\.[a-zA-Z0-9]+$', '', segment_token))
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if str(data.client_host) != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid segment token")

    try:
        segment_data = await fetch_segment_data(str(data.url))
        return StreamingResponse(
            segment_data,
            media_type='application/octet-stream'
        )
    except RetryError as e:
        # Extract the last attempt exception
        last_attempt = e.last_attempt
        if last_attempt.exception():
            raise HTTPException(status_code=500, detail=f"Failed after retries: {str(last_attempt.exception())}")
        raise HTTPException(status_code=500, detail="Unknown error after retries")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
