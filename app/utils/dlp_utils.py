import re


class DLPUtils:
    @staticmethod
    def format_selector(ctx) -> dict:
        """Select the best video and the best audio"""

        # formats are already sorted worst to best
        formats = ctx.get('formats')[::-1]

        # acodec='none' means there is no audio
        best_video = next(f for f in formats
                          if f['vcodec'] != 'none' and f['acodec'] == 'none')

        # find compatible audio extension
        audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
        # vcodec='none' means there is no video
        best_audio = next(f for f in formats if (
                f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

        # These are the minimum required fields for a merged format
        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            # Must be + separated list of protocols
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }

    @staticmethod
    def validate_youtube_video_id(video_id: str) -> bool:
        """
        Validates a YouTube video ID.

        Parameters:
        video_id (str): The YouTube video ID to validate.

        Returns:
        bool: True if the video ID is valid, False otherwise.
        """
        pattern = re.compile(r'^[a-zA-Z0-9_-]{11}$')
        return bool(pattern.match(video_id))
