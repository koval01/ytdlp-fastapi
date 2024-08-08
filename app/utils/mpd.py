from fastapi import Request
from lxml import etree

from app.models.media import VideoFormat, AudioFormat
from app.utils.crypto import Cryptography
from app.utils.filter import Filter


class MPDGenerator:
    def __init__(self, request: Request, videos: list[VideoFormat], audios: list[AudioFormat]) -> None:
        """
        Initialize the MPDGenerator with lists of video and audio formats.

        :param videos: List of video format objects
        :param audios: List of audio format objects
        """
        self.request = request
        self.videos = videos
        self.audios = audios

    def _create_video_adaptation_set(self, parent: etree.Element) -> None:
        """
        Create and append video adaptation sets to the parent XML element.

        :param parent: The parent XML element to append the adaptation sets to
        """
        for video in self.videos:
            adaptation_set = etree.SubElement(parent, 'AdaptationSet', {
                'mimeType': f'video/{video.ext}',
                'codecs': video.vcodec or '',
                'startWithSAP': '1'
            })
            representation = etree.SubElement(adaptation_set, 'Representation', {
                'id': video.format_id,
                'bandwidth': str(int(video.tbr)),
                'width': str(video.width or 0),
                'height': str(video.height or 0),
                'frameRate': str(video.fps or 0)
            })
            base_url = etree.SubElement(representation, 'BaseURL')

            _data = Cryptography().encrypt_json({
                'url': str(video.url),
                'client_host': self.request.client.host
            })
            base_url.text = f"{Filter.scheme(self.request)}://{self.request.url.netloc}/v1/playback/{_data}".encode()

    def _create_audio_adaptation_set(self, parent: etree.Element) -> None:
        """
        Create and append audio adaptation sets to the parent XML element.

        :param parent: The parent XML element to append the adaptation sets to
        """
        for audio in self.audios:
            adaptation_set = etree.SubElement(parent, 'AdaptationSet', {
                'mimeType': f'audio/{audio.ext}',
                'codecs': audio.acodec or '',
                'startWithSAP': '1',
                'lang': audio.language or ''
            })
            representation = etree.SubElement(adaptation_set, 'Representation', {
                'id': audio.format_id,
                'bandwidth': str(int(audio.tbr)),
                'audioSamplingRate': str(audio.asr)
            })
            base_url = etree.SubElement(representation, 'BaseURL')

            _data = Cryptography().encrypt_json({
                'url': str(audio.url),
                'client_host': self.request.client.host
            })
            base_url.text = f"{Filter.scheme(self.request)}://{self.request.url.netloc}/v1/playback/{_data}".encode()

    def generate_mpd(self) -> str:
        """
        Generate an MPEG-DASH MPD manifest.

        :return: The MPD manifest as a string
        """
        mpd = etree.Element('MPD', {
            'xmlns': 'urn:mpeg:dash:schema:mpd:2011',
            'minBufferTime': 'PT1.5S',
            'profiles': 'urn:mpeg:dash:profile:isoff-on-demand:2011',
            'type': 'static'
        })
        period = etree.SubElement(mpd, 'Period')
        self._create_video_adaptation_set(period)
        self._create_audio_adaptation_set(period)
        return etree.tostring(mpd, encoding='utf-8', pretty_print=True).decode('utf-8')
