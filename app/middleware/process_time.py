import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to measure the processing time of requests and add it to the response headers.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{int(process_time * 1000)} ms"
        return response
