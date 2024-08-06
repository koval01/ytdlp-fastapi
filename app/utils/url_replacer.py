import re
from fastapi import Request
from app.utils.crypto import Cryptography


class URLValidator:
    """
    This class provides functionality to validate and replace specific video playback URLs in a given data structure
    with encrypted URLs pointing to a local playback endpoint.
    """

    def __init__(self, request: Request):
        self.request = request
        self.url_pattern = re.compile(
            r"https://rr(?P<host>[^/]+)\.(?:googlevideo|c\.youtube)\.com/videoplayback\?(?P<query>.+)"
        )

    def _replace_url(self, url: str) -> str:
        """
        Replaces a single video playback URL with an encrypted local URL if it matches the pattern.

        Args:
            url: The video playback URL to replace.

        Returns:
            The encrypted local URL if the input URL matches the pattern, otherwise returns the original URL.
        """
        match = self.url_pattern.search(url)
        if match:
            _data = Cryptography().encrypt_json({
                'url': url,
                'client_host': self.request.client.host
            })
            return f"{self.request.url.scheme}://{self.request.url.netloc}/v1/playback/{_data}"
        return url

    def _process_data(self, data: dict | list) -> None:
        """
        Recursively searches through the data structure and replaces video playback URLs if they match the pattern.

        Args:
            data: The data structure to process. Can be a dictionary or a list.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._process_data(value)
                elif isinstance(value, str):
                    data[key] = self._replace_url(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._process_data(item)
                elif isinstance(item, str):
                    data[i] = self._replace_url(item)

    def replace_urls(self, data: dict | list) -> dict | list:
        """
        Replaces all video playback URLs in the given data structure with encrypted local URLs if they match the pattern.

        Args:
            data: The data structure to process. Can be a dictionary or a list.

        Returns:
            The data structure with the URLs replaced if matched.
        """
        self._process_data(data)
        return data
