import platform
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class NodeMiddleware(BaseHTTPMiddleware):
    """
    This middleware adds a header to the response
    with the identifier of the server that processed this request
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Dl-App-Node"] = platform.node()
        return response
