import re
import logging
from typing import Callable
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.config import settings

logger = logging.getLogger("referer_check")

def is_valid_referer(referer: str, allowed_hosts: list[str]) -> bool:
    for host in allowed_hosts:
        if host.startswith("*."):
            domain_pattern = re.escape(host[2:])
            pattern = rf"^(?:.+\.)?{domain_pattern}(:\d+)?$"
            if re.match(pattern, referer):
                return True
        else:
            pattern = rf"^{re.escape(host)}(:\d+)?$"
            if re.match(pattern, referer):
                return True
    return False

class RefererCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith("/v1/"):
            x_secret = request.headers.get("X-Secret")
            referer = request.headers.get("Referer")
            referer = urlparse(referer).netloc

            if x_secret != settings.SECRET_KEY:
                if not referer:
                    logger.warning(f"Blocked request to {request.url.path} due to missing referer")
                    return Response(content=None, status_code=400)

                allowed_hosts = settings.ALLOWED_HOSTS.split(",")
                if not is_valid_referer(referer, allowed_hosts):
                    logger.warning(f"Blocked request to {request.url.path} from invalid referer: {referer}")
                    return Response(content=None, status_code=400)

        response = await call_next(request)
        return response
