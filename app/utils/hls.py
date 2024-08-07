import re

from fastapi import Request

from app.utils.crypto import Cryptography


class HLSReplacer:
    @staticmethod
    def replace_manifest_links(manifest_content, request: Request) -> str:
        manifest_url_pattern = re.compile(
            r'https://manifest\.googlevideo\.com/api/manifest/hls_playlist/expire/.+/playlist/index\.m3u8')
        playback_url_pattern = re.compile(r'https://rr[^/]+\.googlevideo\.com/videoplayback/id/.+')

        def replace_link(match):
            url = match.group(0)
            _data = Cryptography().encrypt_json({
                'url': url,
                'client_host': request.client.host
            })
            if 'hls_playlist' in url:
                return f"{request.url.scheme}://{request.url.netloc}/v1/manifest/hls/{_data}.m3u8"
            else:
                return f"{request.url.scheme}://{request.url.netloc}/v1/manifest/segment/{_data}.ts"

        manifest_content = manifest_url_pattern.sub(replace_link, manifest_content)
        manifest_content = playback_url_pattern.sub(replace_link, manifest_content)

        return manifest_content
