import re

from fastapi import Request

from app.models.ytdlp import YouTubeResponse
from app.utils.config import settings
from app.utils.crypto import Cryptography


class URLValidator:
    """
    This class provides functionality to validate and replace specific video playback URLs
    in a given data structure with encrypted URLs pointing to a local playback endpoint.
    """

    def __init__(self, request: Request) -> None:
        """
        Initialize the URLValidator with the request object and compile regex patterns.

        Args:
            request (Request): The FastAPI request object.
        """
        self.request = request

        # Regex pattern to match video playback URLs
        self.url_pattern_playback = re.compile(
            r"https://rr(?P<host>[^/]+)\.(?:googlevideo|c\.youtube)\.com/videoplayback\?(?P<query>.+)"
        )

        # Regex pattern to match manifest URLs
        self.url_pattern_manifest = re.compile(
            r"https://(?:manifest\.googlevideo\.com|www\.youtube\.com)"
            r"/api/manifest/hls_(?:variant|playlist)/(?P<query>.+)"
        )

        self.crypto = Cryptography()  # Initialize the Cryptography utility

    def _replace_url(self, url: str) -> str:
        """
        Replaces a single video playback or manifest URL with an encrypted local URL if it matches the pattern.

        Args:
            url (str): The video playback or manifest URL to replace.

        Returns:
            str: The encrypted local URL if the input URL matches the pattern, otherwise the original URL.
        """
        # Match video playback URL pattern
        match_playback = self.url_pattern_playback.search(url)

        # Determine the client host for encryption
        client_host = self.request.client.host
        x_host = self.request.headers.get("X-Client-Host")
        if settings.REST_MODE and x_host:
            client_host = x_host

        # Replace video playback URL if matched
        if match_playback:
            encrypted_data = self.crypto.encrypt_json({
                'url': url,
                'client_host': client_host
            })
            return f"{self.request.url.scheme}://{self.request.url.netloc}/v1/playback/{encrypted_data}"

        # Match manifest URL pattern
        match_manifest = self.url_pattern_manifest.search(url)

        # Replace manifest URL if matched
        if match_manifest:
            encrypted_data = self.crypto.encrypt_json({
                'url': url,
                'client_host': client_host
            })
            return f"{self.request.url.scheme}://{self.request.url.netloc}/v1/manifest/hls/{encrypted_data}"

        # Return the original URL if no pattern matched
        return url

    def _process_data(self, data: dict | list) -> None:
        """
        Recursively searches through the data structure and replaces URLs if they match the pattern.

        Args:
            data (dict | list): The data structure to process. Can be a dictionary or a list.
        """
        if isinstance(data, dict):
            # Iterate through dictionary items
            for key, value in data.items():
                if isinstance(value, str):
                    # Replace URL if value is a string
                    data[key] = self._replace_url(value)
                elif isinstance(value, (dict, list)):
                    # Recursively process nested dictionaries or lists
                    self._process_data(value)

            # Special handling for 'formats' key in the data
            if 'formats' in data:
                filtered_formats = [
                    item for item in data['formats']
                    if item['video_ext'] == "mp4" and item['protocol'] == "m3u8_native"
                ]
                if filtered_formats:
                    last_format = filtered_formats[-1]
                    manifest_url = last_format.get('manifest_url')
                    if manifest_url:
                        data['manifest_url'] = self._replace_url(manifest_url)
                # Remove 'formats' key from the data after processing
                del data['formats']

        elif isinstance(data, list):
            # Iterate through list items
            for i, item in enumerate(data):
                if isinstance(item, str):
                    # Replace URL if item is a string
                    data[i] = self._replace_url(item)
                elif isinstance(item, (dict, list)):
                    # Recursively process nested dictionaries or lists
                    self._process_data(item)

    def replace_urls(self, data: dict | list) -> YouTubeResponse:
        """
        Replaces all video playback URLs in the given data structure with encrypted local URLs
        if they match the pattern.

        Args:
            data (dict | list): The data structure to process. Can be a dictionary or a list.

        Returns:
            YouTubeResponse: The data structure with the URLs replaced if matched.
        """
        # Process the data to replace URLs
        self._process_data(data)
        # Return the processed data as a YouTubeResponse object
        return YouTubeResponse(**data)
