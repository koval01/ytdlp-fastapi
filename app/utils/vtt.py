from typing import List

from fastapi import Request

from app.models.storyboard import Fragment
from app.utils.crypto import Cryptography
from app.utils.filter import Filter


class VTTConverter:
    """
    A class to convert a list of fragments to WebVTT format.

    Attributes:
        fragments (List[Fragment]): A list of fragment objects each containing URL and duration.
        request (Request): A FastAPI request object used to generate image URLs.
    """

    def __init__(self, fragments: List[Fragment], request: Request):
        """
        Initialize the VTTConverter with fragments and a request object.

        Args:
            fragments (List[Fragment]): A list of fragment objects.
            request (Request): A FastAPI request object.
        """
        self.fragments = fragments
        self.request = request

    @staticmethod
    def seconds_to_timestamp(seconds: float) -> str:
        """
        Convert a time duration in seconds to a timestamp format for VTT.

        Args:
            seconds (float): Time duration in seconds.

        Returns:
            str: Timestamp in the format "HH:MM:SS.MMM".
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = (seconds - int(seconds)) * 1000
        return f"{hours:02}:{minutes:02}:{int(seconds):02}.{int(milliseconds):03}"

    def convert_to_vtt(self) -> str:
        """
        Convert the list of fragments to WebVTT format.

        Returns:
            str: A string in WebVTT format.
        """
        vtt_content = "WEBVTT\n\n"
        current_time = 0

        for i, fragment in enumerate(self.fragments):
            _data = Cryptography().encrypt_json({
                'url': str(fragment.url),
                'client_host': self.request.client.host
            })
            url = f"{Filter.scheme(self.request)}://{self.request.url.netloc}/image/{_data}"
            start_time = self.seconds_to_timestamp(current_time)
            end_time = self.seconds_to_timestamp(current_time + fragment.duration)
            vtt_content += f"{i + 1}\n"
            vtt_content += f"{start_time} --> {end_time}\n"
            vtt_content += f"{url}\n\n"
            current_time += fragment.duration

        return vtt_content
