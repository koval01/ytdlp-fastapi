from typing import List, Optional, Dict, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Format(BaseModel):
    format: str
    format_id: str
    ext: str
    protocol: str
    language: Optional[str]
    format_note: Optional[str]
    filesize_approx: Optional[int]
    tbr: Optional[float]
    width: Optional[int]
    height: Optional[int]
    resolution: Optional[str]
    fps: Optional[float]
    dynamic_range: Optional[str]
    vcodec: Optional[str]
    vbr: Optional[float]
    stretched_ratio: Optional[float]
    aspect_ratio: Optional[float]
    acodec: Optional[str]
    abr: Optional[float]
    asr: Optional[int]
    audio_channels: Optional[int]
    manifest_url: Optional[HttpUrl]


class YouTubeResponse(BaseModel):
    id: str
    title: str
    thumbnail: str
    description: str
    channel_id: str
    channel_url: HttpUrl
    duration: int
    view_count: int
    age_limit: int
    categories: List[str]
    tags: List[str]
    comment_count: int
    like_count: int
    channel: str
    channel_follower_count: int
    channel_is_verified: Optional[bool] = False
    uploader: str
    uploader_id: str
    uploader_url: HttpUrl
    upload_date: str
    timestamp: int
    availability: str
    manifest_url: HttpUrl
    display_id: str
    fulltitle: str
    duration_string: str
    is_live: bool
    was_live: bool
    epoch: int
    formats: List[Format] = Field(default_factory=list)

    @field_validator('formats')
    def parse_formats(cls, value: Union[List[Dict], Dict]) -> List[Format]:
        if isinstance(value, dict):
            return [Format(**value)]
        return [Format(**f) for f in value]
