"""Models."""

from datetime import datetime

from pydantic import BaseModel
from slugify import slugify


class Channel(BaseModel):
    """YouTube Channel model."""

    channel_id: str
    handle: str
    title: str
    description: str
    upload_playlist_id: str
    video_count: int
    subscriber_count: int | None

    def __str__(self) -> str:
        """Represent string."""
        return f"{self.title}"

    @property
    def filename(self) -> str:
        """Filename."""
        return f"{slugify(self.title)}-{self.channel_id}"


class Video(BaseModel):
    """Youtube video model."""

    video_id: str
    published_at: datetime
    title: str
    view_count: int
    like_count: int
    thumbnail_url: str
    thumbnail_width: int
    thumbnail_height: int

    def __str__(self) -> str:
        """Represent string."""
        return f"{self.title}"

    @property
    def fileformat(self) -> str:
        """Fileformat (e.g. .jpg)"""
        return self.thumbnail_url.split(".")[-1]

    @property
    def filename(self) -> str:
        """Filename."""
        return f"{slugify(self.title)}-{self.video_id}.{self.fileformat}"


class VideoList(BaseModel):
    """Video list for saving data."""

    __root__: list[Video]
