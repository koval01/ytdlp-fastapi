import re
from fastapi.logger import logger
from typing import Callable
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.config import settings


def is_valid_referer_or_origin(host: str, allowed_hosts: list[str]) -> bool:
    """
    Validates the referer or origin against a list of allowed hosts.

    Args:
        host (str): The host domain to be checked.
        allowed_hosts (list[str]): A list of allowed host patterns.

    Returns:
        bool: True if the host is valid, False otherwise.
    """
    for allowed_host in allowed_hosts:
        if allowed_host.startswith("*."):
            # Pattern to match subdomains
            domain_pattern = re.escape(allowed_host[2:])
            pattern = rf"^(?:.+\.)?{domain_pattern}(:\d+)?$"
            if re.match(pattern, host):
                return True
        else:
            # Exact match pattern
            pattern = rf"^{re.escape(allowed_host)}(:\d+)?$"
            if re.match(pattern, host):
                return True
    return False


class RefererCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check the 'Referer' or 'Origin' headers for certain routes and validate them against allowed hosts.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processes incoming requests, checking the 'Referer' or 'Origin' headers for specific paths.

        Args:
            request (Request): The incoming request object.
            call_next (Callable): The next middleware or route handler.

        Returns:
            Response: The response object, or a 400 status code if validation fails.
        """
        # Apply referer check only to specific paths (e.g., those starting with /v1/)
        if request.url.path.startswith("/v1/"):
            x_secret = request.headers.get("X-Secret")

            if bool(settings.DISABLE_TURNSTILE) and x_secret == settings.SECRET_KEY:
                response = await call_next(request)
                return response

            referer = request.headers.get("Referer")
            origin = request.headers.get("Origin")

            # Extract the netloc (domain) from the referer or origin URL
            host = urlparse(referer).netloc if referer else urlparse(origin).netloc

            # Check if the secret key matches; if not, validate the referer or origin
            if not request.url.path.startswith("/v1/video/"):
                if not host:
                    logger.warning(f"Blocked request to {request.url.path} due to missing referer or origin")
                    return Response(content=None, status_code=400)

                # Split allowed hosts from settings and validate the referer or origin
                allowed_hosts = settings.ALLOWED_HOSTS.split(",")
                if not is_valid_referer_or_origin(host, allowed_hosts):
                    logger.warning(f"Blocked request to {request.url.path} from invalid referer or origin: {host}")
                    return Response(content=None, status_code=400)

        # Proceed with the request if validation passes
        response = await call_next(request)
        return response
