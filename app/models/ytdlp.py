from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, AliasChoices


class Comment(BaseModel):
    id: str
    parent: Optional[str] = "root"
    text: str
    like_count: Optional[int] = 0
    author_id: str
    author: str
    author_thumbnail: Optional[HttpUrl] = None
    author_is_uploader: Optional[bool] = False
    author_is_verified: Optional[bool] = False
    author_url: Optional[HttpUrl] = None
    is_favorited: Optional[bool] = False
    timestamp: int
    is_pinned: Optional[bool] = False
    time_text: str = Field(validation_alias=AliasChoices('_time_text'))

class YouTubeResponse(BaseModel):
    id: str
    title: str
    thumbnail: HttpUrl
    description: Optional[str] = None
    channel_id: str
    channel_url: HttpUrl
    duration: Optional[int] = None
    view_count: int
    age_limit: int
    categories: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    comment_count: Optional[int] = None
    like_count: Optional[int] = 0
    channel: str
    channel_id: str = Field(validation_alias=AliasChoices('uploader_id'))
    channel_follower_count: Optional[int] = None
    channel_is_verified: Optional[bool] = False
    channel_url: HttpUrl = Field(validation_alias=AliasChoices('uploader_url'))
    upload_date: str
    timestamp: Optional[int] = None
    availability: Optional[str] = None
    manifest_url: HttpUrl
    display_id: str
    full_title: str = Field(validation_alias=AliasChoices('fulltitle'))
    duration_string: Optional[str] = None
    is_live: bool
    was_live: bool
    epoch: int
    resolution: Optional[str] = None
    fps: Optional[int] = None
    filesize_approx: Optional[int] = None
    comments: Optional[List[Comment]] = []
