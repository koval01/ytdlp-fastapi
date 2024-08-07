from pydantic import BaseModel, HttpUrl
from typing import Optional


class VideoFormat(BaseModel):
    asr: Optional[int]
    filesize: int
    format_id: str
    format_note: str
    source_preference: Optional[int]
    fps: Optional[int]
    audio_channels: Optional[int]
    height: Optional[int]
    quality: int
    has_drm: bool
    tbr: float
    filesize_approx: int
    url: HttpUrl
    width: Optional[int]
    language: Optional[str]
    language_preference: Optional[int]
    preference: Optional[int]
    ext: str
    vcodec: Optional[str]
    acodec: Optional[str]
    dynamic_range: Optional[str]
    container: str
    protocol: str
    resolution: str
    aspect_ratio: Optional[float]
    video_ext: Optional[str]
    audio_ext: Optional[str]
    abr: Optional[float]
    vbr: Optional[float]
    format: str


class AudioFormat(BaseModel):
    asr: int
    filesize: int
    format_id: str
    format_note: str
    source_preference: Optional[int]
    fps: Optional[int]
    audio_channels: int
    height: Optional[int]
    quality: int | float
    has_drm: bool
    tbr: float
    filesize_approx: int
    url: HttpUrl
    width: Optional[int]
    language: str
    language_preference: Optional[int]
    preference: Optional[int]
    ext: str
    vcodec: Optional[str]
    acodec: Optional[str]
    dynamic_range: Optional[str]
    container: str
    protocol: str
    resolution: str
    aspect_ratio: Optional[float]
    video_ext: Optional[str]
    audio_ext: Optional[str]
    abr: Optional[float]
    vbr: Optional[float]
    format: str
