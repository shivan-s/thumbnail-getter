"""Channel."""


import httpx
from bs4 import BeautifulSoup
from fastapi import status

from app.models import Channel
from app.utils import parse_handle
from app.utils.defaults import YOUTUBE_URL

from .api import api


def get_channel_id(handle: str) -> str | None:
    """Obtain a channel ID."""
    handle = parse_handle(handle)
    r = httpx.get(f"{YOUTUBE_URL}{handle}")
    if r.status_code == status.HTTP_200_OK:
        soup = BeautifulSoup(r.content, "html.parser")
        channel_id = soup.find("meta", attrs={"itemprop": "channelId"}).get(
            "content"
        )
        return channel_id
    return None


def get_channel_data(handle: str) -> Channel:
    """Obtain channel data."""
    channel_id = get_channel_id(handle)
    response = (
        api.channels()
        .list(
            part="snippet,contentDetails,statistics",
            id=channel_id,
        )
        .execute()
    )
    channel_data = response["items"][0]
    channel = Channel(
        channel_id=channel_id,
        handle=parse_handle(handle),
        title=channel_data["snippet"]["title"],
        description=channel_data["snippet"]["description"],
        subscriber_count=channel_data["statistics"].get("subscriberCount"),
        video_count=channel_data["statistics"]["videoCount"],
        upload_playlist_id=channel_data["contentDetails"]["relatedPlaylists"][
            "uploads"
        ],
    )
    return channel
