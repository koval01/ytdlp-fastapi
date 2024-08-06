from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl


class Format(BaseModel):
    format_id: str
    format_note: Optional[str] = None
    url: HttpUrl
    protocol: str
    ext: str
    asr: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int | float] = None
    tbr: Optional[float]  # average bitrate in Kbps
    abr: Optional[float]  # average bitrate for audio in Kbps
    filesize: Optional[int] = None  # in bytes
    bitrate: Optional[int] = None  # in bps
    language: Optional[str] = None
    dynamic_range: Optional[str] = None
    container: Optional[str] = None
    has_drm: Optional[bool] = None
    quality: Optional[int | float] = None
    resolution: Optional[str]
    aspect_ratio: Optional[float]


class Thumbnail(BaseModel):
    url: HttpUrl
    preference: Optional[int]
    id: Optional[str]


class Chapter(BaseModel):
    start_time: float
    end_time: float
    title: str


class Heatmap(BaseModel):
    start_time: float
    end_time: float
    value: float


class YouTubeResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    duration: Optional[int]  # Duration in seconds
    duration_string: Optional[str]
    upload_date: Optional[str]  # Date in YYYYMMDD format
    uploader: Optional[str]
    uploader_id: Optional[str]
    uploader_url: Optional[HttpUrl]
    channel: Optional[str]
    channel_id: Optional[str]
    channel_follower_count: Optional[int]
    channel_is_verified: Optional[bool]
    channel_url: Optional[HttpUrl]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    tags: Optional[List[str]]
    categories: Optional[List[str]]
    thumbnails: Optional[List[Thumbnail]]
    thumbnail: Optional[HttpUrl]
    formats: Optional[List[Format]]
    requested_formats: Optional[List[Format]]
    subtitles: Optional[Dict[str, List[Dict]]]  # Placeholder for subtitle info
    requested_subtitles: Optional[Dict[str, List[Dict]]]  # Placeholder for requested subtitles info
    chapters: Optional[List[Chapter]]
    heatmap: Optional[List[Heatmap]]
    age_limit: Optional[int]
    availability: Optional[str]
    average_rating: Optional[float]
    is_live: Optional[bool]
    live_status: Optional[str]
    playable_in_embed: Optional[bool]
    original_url: Optional[HttpUrl]
    webpage_url: Optional[HttpUrl]
    webpage_url_basename: Optional[str]
    webpage_url_domain: Optional[str]
    protocol: Optional[str]
    release_timestamp: Optional[int]
    release_year: Optional[int]
    _format_sort_fields: Optional[List[str]]
    _has_drm: Optional[bool]
    epoch: Optional[int]
    extractor: Optional[str]
    extractor_key: Optional[str]
    display_id: Optional[str]
    format_id: Optional[str]
    ext: Optional[str]
    extractor: Optional[str]
    extractor_key: Optional[str]
    playlist: Optional[HttpUrl]
    playlist_index: Optional[int]
    was_live: Optional[bool]
