from typing import AsyncGenerator, Tuple

import aiohttp

from fastapi import HTTPException, Request, status
from fastapi.responses import StreamingResponse


class RangeRequestHandler:
    def __init__(self, url: str):
        self.url = url

    async def fetch_video_data(self, start: int, end: int, chunk_size: int = 10_000) -> AsyncGenerator[bytes, None]:
        """
        Fetch video data from a URL within the specified byte range.

        Args:
            start (int): The starting byte position.
            end (int): The ending byte position.
            chunk_size (int): The size of each chunk to fetch. Defaults to 10,000 bytes.

        Yields:
            AsyncGenerator[bytes, None]: Chunks of video data.
        """
        headers = {"Range": f"bytes={start}-{end}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                if response.status == 416:
                    raise HTTPException(
                        status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                        detail=f"Invalid request range (Range: bytes={start}-{end})",
                    )
                while True:
                    chunk = await response.content.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

    @staticmethod
    def _get_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
        """
        Parse the range header to determine the byte range requested.

        Args:
            range_header (str): The value of the Range header.
            file_size (int): The total size of the file.

        Returns:
            Tuple[int, int]: The start and end byte positions.

        Raises:
            HTTPException: If the range is invalid.
        """

        def _invalid_range():
            return HTTPException(
                status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail=f"Invalid request range (Range:{range_header!r})",
            )

        try:
            h = range_header.replace("bytes=", "").split("-")
            start = int(h[0]) if h[0] != "" else 0
            end = int(h[1]) if h[1] != "" else file_size - 1
        except ValueError:
            raise _invalid_range()

        if start > end or start < 0 or end > file_size - 1:
            raise _invalid_range()
        return start, end

    async def range_requests_response(self, request: Request, content_type: str):
        """
        Handle range requests and return a StreamingResponse with the appropriate byte range.

        Args:
            request (Request): The HTTP request object.
            content_type (str): The content type of the response.

        Returns:
            StreamingResponse: The response object with the requested byte range.

        Raises:
            HTTPException: If the file is not found or other errors occur.
        """
        async with aiohttp.ClientSession() as session:
            async with session.head(self.url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
                file_size = int(response.headers.get("Content-Length", 0))

        range_header = request.headers.get("range")

        headers = {
            "content-type": content_type,
            "accept-ranges": "bytes",
            "content-encoding": "identity",
            "content-length": str(file_size),
            "access-control-expose-headers": (
                "content-type, accept-ranges, content-length, "
                "content-range, content-encoding"
            ),
        }
        start = 0
        end = file_size - 1
        status_code = status.HTTP_200_OK

        if range_header is not None:
            start, end = self._get_range_header(range_header, file_size)
            size = end - start + 1
            headers["content-length"] = str(size)
            headers["content-range"] = f"bytes {start}-{end}/{file_size}"
            status_code = status.HTTP_206_PARTIAL_CONTENT

        return StreamingResponse(
            self.fetch_video_data(start, end),
            headers=headers,
            status_code=status_code,
        )
