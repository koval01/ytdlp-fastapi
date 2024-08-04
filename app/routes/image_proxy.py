"""
Route handler for /image/{image_token}
"""

from cryptography.fernet import InvalidToken
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.models.error import HTTPError
from app.models.image import Image
from app.utils.crypto import Cryptography
from aiohttp import ClientSession
from io import BytesIO

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
        data = Image(**data)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if data.client_host != request.client.host:
        raise HTTPException(status_code=400, detail="Invalid image token")

    async with ClientSession() as session:
        try:
            async with session.get(data.url) as response:
                response.raise_for_status()
                image_data = BytesIO(await response.read())
                return StreamingResponse(
                    image_data,
                    media_type=response.headers.get('Content-Type', 'image/jpeg')
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
