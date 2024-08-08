import re
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.config import settings


def is_valid_referer(referer: str, allowed_hosts: list[str]) -> bool:
    """
    Check if the referer is valid based on the allowed hosts.

    Parameters:
    - referer (str): The referer URL to validate.
    - allowed_hosts (list[str]): List of allowed domains (can include wildcards).

    Returns:
    - bool: True if the referer is valid, False otherwise.
    """
    for host in allowed_hosts:
        if host.startswith("*."):
            pattern = re.escape(host[2:]) + r"$"
            if re.search(r"https?://[^/]*\." + pattern, referer):
                return True
        else:
            if re.search(rf"https?://{re.escape(host)}(:[0-9]+)?/", referer):
                return True
    return False


class RefererCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check the Referer header for specific routes.

    This middleware will check the Referer header for requests with paths starting
    with `/v1/`. If the `X-Secret` header is missing or invalid, it will validate the
    Referer header against allowed domains specified in settings.ALLOWED_HOSTS.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith("/v1/"):
            x_secret = request.headers.get("X-Secret")
            referer = request.headers.get("Referer")

            if x_secret != settings.SECRET_KEY:
                if not referer:
                    return Response(content=None, status_code=400)

                allowed_hosts = settings.ALLOWED_HOSTS.split(",")
                if not is_valid_referer(referer, allowed_hosts):
                    return Response(content=None, status_code=400)

        response = await call_next(request)
        return response
