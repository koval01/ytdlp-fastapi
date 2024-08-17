from fastapi import FastAPI, Request, Response
from fastapi.logger import logger
from functools import wraps

from app.utils.config import settings
from app.utils.sign import CustomHasher

app = FastAPI()


def sign_validator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if request and not bool(settings.DISABLE_SIGN):
            client_sign = request.headers.get("X-Sign")
            if not client_sign:
                logger.warning(f"X-Sign header not defined for {request.url}")
                return Response(status_code=400)

            try:
                _hash = CustomHasher().custom_hash(str(request.url))
            except Exception as e:
                logger.warning(f"Error generating hash for {request.url}. Exception: {e}")
                return Response(status_code=400)

            if _hash != client_sign:
                logger.warning(f"Invalid hash for {request.url}")
                return Response(status_code=400)

        response: Response = await func(*args, **kwargs)
        return response

    return wrapper
