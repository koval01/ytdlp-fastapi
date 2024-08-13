import re
import logging
from typing import Callable
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.config import settings

# Initialize logger for referer check middleware
logger = logging.getLogger("referer_check")

def is_valid_referer(referer: str, allowed_hosts: list[str]) -> bool:
    """
    Validates the referer against a list of allowed hosts.

    Args:
        referer (str): The referer domain to be checked.
        allowed_hosts (list[str]): A list of allowed host patterns.

    Returns:
        bool: True if the referer is valid, False otherwise.
    """
    for host in allowed_hosts:
        if host.startswith("*."):
            # Pattern to match subdomains
            domain_pattern = re.escape(host[2:])
            pattern = rf"^(?:.+\.)?{domain_pattern}(:\d+)?$"
            if re.match(pattern, referer):
                return True
        else:
            # Exact match pattern
            pattern = rf"^{re.escape(host)}(:\d+)?$"
            if re.match(pattern, referer):
                return True
    return False

class RefererCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check the 'Referer' header for certain routes and validate it against allowed hosts.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processes incoming requests, checking the 'Referer' header for specific paths.

        Args:
            request (Request): The incoming request object.
            call_next (Callable): The next middleware or route handler.

        Returns:
            Response: The response object, or a 400 status code if validation fails.
        """
        # Apply referer check only to specific paths (e.g., those starting with /v1/)
        if request.url.path.startswith("/v1/"):
            # Retrieve the 'X-Secret' and 'Referer' headers
            x_secret = request.headers.get("X-Secret")
            referer = request.headers.get("Referer")
            referer = urlparse(referer).netloc  # Extract the netloc (domain) from the referer URL

            # Check if the secret key matches; if not, validate the referer
            if x_secret != settings.SECRET_KEY:
                if not referer:
                    logger.warning(f"Blocked request to {request.url.path} due to missing referer")
                    return Response(content=None, status_code=400)

                # Split allowed hosts from settings and validate the referer
                allowed_hosts = settings.ALLOWED_HOSTS.split(",")
                if not is_valid_referer(referer, allowed_hosts):
                    logger.warning(f"Blocked request to {request.url.path} from invalid referer: {referer}")
                    return Response(content=None, status_code=400)

        # Proceed with the request if validation passes
        response = await call_next(request)
        return response
