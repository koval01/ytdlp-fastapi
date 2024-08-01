import re

from fastapi import Request

from utils.crypto import Cryptography


class URLReplacer:
    """
    This class provides functionality to replace Google Video URLs in a given data structure
    with encrypted URLs pointing to a local playback endpoint.
    """

    def __init__(self, request: Request):
        self.request = request
        self.url_pattern = re.compile(r"https://rr(?P<host>[^/]+)\.googlevideo\.com/videoplayback\?(?P<query>.+)")

    def _replace_url(self, url: str) -> str:
        """
        Replaces a single Google Video URL with an encrypted local URL.

        Args:
            url: The Google Video URL to replace.

        Returns:
            The encrypted local URL.
        """
        match = self.url_pattern.search(url)
        if match:
            _data = Cryptography().encrypt_json({
                'host': match.group('host'),
                'query': match.group('query'),
                'client_host': self.request.client.host
            })
            return f"http://{self.request.url.netloc}/v1/playback/{_data}"
        return url

    def _process_data(self, data: dict | list) -> None:
        """
        Recursively searches through the data structure and replaces Google Video URLs.

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
        Replaces all Google Video URLs in the given data structure with encrypted local URLs.

        Args:
            data: The data structure to process. Can be a dictionary or a list.

        Returns:
            The data structure with the URLs replaced.
        """
        self._process_data(data)
        return data
