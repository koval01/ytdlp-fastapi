"""
Route handler for /image/{image_token}
"""

from io import BytesIO

from aiohttp import ClientSession
from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from yarl import URL

from app.models.crypto import CryptoObject
from app.models.error import HTTPError
from app.utils.crypto import Cryptography

router = APIRouter()


@router.get(
    "/image/{image_token}",
    summary="Get image from Google network",
    responses={
        200: {"content": {
            "image/webp": {}
        }},
        400: {"model": HTTPError},
        500: {"model": HTTPError}
    },
    tags=["Util"]
)
async def image(request: Request, image_token: str) -> StreamingResponse:
    """Request handler"""
    try:
        data = Cryptography().decrypt_json(image_token)
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Invalid image token")

    try:
        data = CryptoObject(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=e.__name__)

    if str(data.client_host) != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid image token")

    async with ClientSession() as session:
        try:
            async with session.get(URL(str(data.url), encoded=True)) as response:
                response.raise_for_status()
                image_data = BytesIO(await response.read())
                return StreamingResponse(
                    image_data,
                    media_type=response.headers.get('Content-Type', 'image/jpeg')
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e.__name__)
