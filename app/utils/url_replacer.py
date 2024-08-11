import re

from fastapi import Request

from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.crypto import Cryptography
from app.utils.filter import Filter


class URLValidator:
    """
    This class provides functionality to validate and replace specific video playback URLs in a given data structure
    with encrypted URLs pointing to a local playback endpoint.
    """

    def __init__(self, request: Request) -> None:
        self.request = request
        self.hls_mode = bool(settings.HLS_MODE)
        self.url_pattern_playback = re.compile(
            r"https://rr(?P<host>[^/]+)\.(?:googlevideo|c\.youtube)\.com/videoplayback\?(?P<query>.+)"
        )
        self.url_pattern_manifest = re.compile(
            r"https://(?:manifest\.googlevideo\.com|www\.youtube\.com)"
            r"/api/manifest/hls_(?:variant|playlist)/(?P<query>.+)"
        )
        self.crypto = Cryptography()

    def _replace_url(self, url: str) -> str:
        """
        Replaces a single video playback URL with an encrypted local URL if it matches the pattern.

        Args:
            url: The video playback URL to replace.

        Returns:
            The encrypted local URL if the input URL matches the pattern, otherwise returns the original URL.
        """
        match_playback = self.url_pattern_playback.search(url)

        client_host = self.request.client.host
        x_host = self.request.headers.get("X-Client-Host")
        if settings.REST_MODE and x_host:
            client_host = x_host

        if match_playback:
            _data = self.crypto.encrypt_json({
                'url': url,
                'client_host': client_host
            })
            return f"{Filter.scheme(self.request)}://{self.request.url.netloc}/v1/playback/{_data}"

        match_manifest = self.url_pattern_manifest.search(url)
        if match_manifest:
            _data = self.crypto.encrypt_json({
                'url': url,
                'client_host': client_host
            })
            return f"{Filter.scheme(self.request)}://{self.request.url.netloc}/v1/manifest/hls/{_data}"

        return url

    def _process_data(self, data: dict | list) -> None:
        """
        Recursively searches through the data structure and replaces video playback URLs if they match the pattern.

        Args:
            data: The data structure to process. Can be a dictionary or a list.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = self._replace_url(value)
                elif isinstance(value, (dict, list)):
                    self._process_data(value)
            if self.hls_mode and 'formats' in data:
                filtered_formats = [
                    item for item in data['formats']
                    if item['video_ext'] == "mp4" and item['protocol'] == "m3u8_native"
                ]
                if filtered_formats:
                    last_format = filtered_formats[-1]
                    manifest_url = last_format.get('manifest_url')
                    if manifest_url:
                        data['manifest_url'] = self._replace_url(manifest_url)
                del data['formats']
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = self._replace_url(item)
                elif isinstance(item, (dict, list)):
                    self._process_data(item)

    def replace_urls(self, data: dict | list) -> YouTubeResponse:
        """
        Replaces all video playback URLs in the given data structure with encrypted local URLs
        if they match the pattern.

        Args:
            data: The data structure to process. Can be a dictionary or a list.

        Returns:
            The data structure with the URLs replaced if matched.
        """
        self._process_data(data)
        return YouTubeResponse(**data)
