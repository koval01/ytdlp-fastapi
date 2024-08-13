import m3u8
from fastapi import Request

from app.utils.config import settings
from app.utils.crypto import Cryptography


class HLSReplacer:
    """
    This class provides functionality to replace HLS manifest URLs with encrypted URLs
    that point to local endpoints, enhancing security and controlling access.
    """

    @staticmethod
    def replace_manifest_links(manifest_content: str, request: Request) -> str:
        """
        Replaces the URLs in an HLS playlist manifest with encrypted local URLs.

        Args:
            manifest_content (str): The original HLS manifest content as a string.
            request (Request): The FastAPI request object.

        Returns:
            str: The updated HLS manifest content with replaced URLs.
        """
        playlist = m3u8.loads(manifest_content)  # Parse the manifest content
        cryptography = Cryptography()  # Initialize the Cryptography utility

        # Determine the client host for encryption
        client_host = request.client.host
        x_host = request.headers.get("X-Client-Host")
        if settings.REST_MODE and x_host:
            client_host = x_host

        def replace_url(url: str) -> str:
            """
            Constructs and returns a new encrypted URL for a given HLS segment or playlist.

            Args:
                url (str): The original URL to be replaced.

            Returns:
                str: The new encrypted URL.
            """
            _host = f"{request.url.scheme}://{request.url.netloc}"
            _data = cryptography.encrypt_json({
                'url': url,
                'client_host': client_host
            })

            # Determine the new URL based on the type (playlist or segment)
            if 'hls_playlist' in url:
                new_url = f"{_host}/v1/manifest/hls/{_data}.m3u8"
            else:
                new_url = f"{_host}/v1/manifest/segment/{_data}.ts"

            return new_url

        # Replace URLs in segments and associated keys
        if playlist.segments:
            for segment in playlist.segments:
                segment.uri = replace_url(segment.uri)  # Replace segment URL

                # Replace key URL if present
                if segment.key and segment.key.uri:
                    segment.key.uri = replace_url(segment.key.uri)

                # Replace initialization section URL if present
                if segment.init_section and segment.init_section.uri:
                    segment.init_section.uri = replace_url(segment.init_section.uri)

        # Replace URLs in media segments
        if playlist.media:
            for media in playlist.media:
                media.uri = replace_url(media.uri)

        # Optimize and replace URLs in resolution groups
        resolution_groups = {}
        i = 0
        while i < len(playlist.playlists):
            p = playlist.playlists[i]

            # Filter out non-MP4 (e.g., VP9) streams
            if 'vp09' not in p.stream_info.codecs:
                del playlist.playlists[i]
                continue  # Skip incrementing i to check the next item at the same index

            resolution = p.stream_info.resolution
            if resolution not in resolution_groups:
                # Add a new resolution group if it doesn't exist
                resolution_groups[resolution] = p
                p.uri = replace_url(p.uri)
                i += 1
            else:
                existing_playlist = resolution_groups[resolution]
                if p.stream_info.bandwidth > existing_playlist.stream_info.bandwidth:
                    # Replace the existing playlist with a higher bandwidth one
                    resolution_groups[resolution] = p
                    p.uri = replace_url(p.uri)
                    del playlist.playlists[i]
                else:
                    # Remove the current playlist if a better one already exists
                    del playlist.playlists[i]

        # Return the updated manifest content as a string
        updated_manifest = playlist.dumps()
        return updated_manifest
