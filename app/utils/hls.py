import m3u8
from fastapi import Request
from app.utils.crypto import Cryptography


class HLSReplacer:
    @staticmethod
    def replace_manifest_links(manifest_content, request: Request) -> str:
        playlist = m3u8.loads(manifest_content)

        # Function to replace URLs in the playlist
        def replace_url(url):
            _data = Cryptography().encrypt_json({
                'url': url,
                'client_host': request.client.host
            })

            # Construct the new URL based on the type
            if 'hls_playlist' in url:
                new_url = f"{request.url.scheme}://{request.url.netloc}/v1/manifest/hls/{_data}.m3u8"
            else:
                new_url = f"{request.url.scheme}://{request.url.netloc}/v1/manifest/segment/{_data}.ts"

            return new_url

        # Replace URLs in segments and key URLs
        if playlist.segments:
            for segment in playlist.segments:
                segment.uri = replace_url(segment.uri)

                if segment.key and segment.key.uri:
                    segment.key.uri = replace_url(segment.key.uri)

                if segment.init_section and segment.init_section.uri:
                    segment.init_section.uri = replace_url(segment.init_section.uri)

        # Replace URLs in media
        if playlist.media:
            for media in playlist.media:
                media.uri = replace_url(media.uri)

        i = 0
        resolution_groups = {}
        while i < len(playlist.playlists):
            p = playlist.playlists[i]
            if 'vp09' not in p.stream_info.codecs:
                del playlist.playlists[i]  # Remove the item if 'vp09' is not in the codecs
                # Do not increment i because the next item now occupies the current index
            else:
                resolution = p.stream_info.resolution
                if resolution not in resolution_groups:
                    resolution_groups[resolution] = p
                    p.uri = replace_url(p.uri)  # Update the URI if the item is kept
                    i += 1  # Move to the next item if the current item was kept
                else:
                    # Compare and keep the one with the higher bandwidth
                    existing_playlist = resolution_groups[resolution]
                    if p.stream_info.bandwidth > existing_playlist.stream_info.bandwidth:
                        # Replace the existing playlist with the new one
                        resolution_groups[resolution] = p
                        p.uri = replace_url(p.uri)  # Update the URI if the item is kept
                        del playlist.playlists[i]  # Remove the old playlist with lower bandwidth
                        # Do not increment i because the next item now occupies the current index
                    else:
                        del playlist.playlists[i]  # Remove the item if it has lower bandwidth
                        # Do not increment i because the next item now occupies the current index

        # Return the updated manifest content
        updated_manifest = playlist.dumps()
        return updated_manifest
