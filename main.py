from typing import Literal

from fastapi import FastAPI

import yt_dlp
import re

app = FastAPI()


@app.get("/{service}/{content_id}")
def get(service: Literal["youtube", "twitch"], content_id: str):
    services = {
        "youtube": "www.youtube.com/watch?v=",
        "twitch": "www.twitch.tv/"
    }
    with yt_dlp.YoutubeDL({}) as ydl:
        try:
            return ydl.extract_info(f"https://{services[service]}{content_id}", download=False)
        except Exception as e:
            error = re.search(r"\[.*?] (.+): (.+)", str(e))
            return {"error": error.group(2), "id": error.group(1)}
