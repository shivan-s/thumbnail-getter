"""Video."""

from fastapi import HTTPException, status

from app.models import Channel, Video
from app.settings import LIMIT

from .api import api


def get_video_data(channel: Channel) -> list[Video]:
    """Get videos data and download thumbnails from a channel.

    Args:
        channel (Channel): YouTube channel of interested.

    Returns:
        VideoList: List of video data.
    """

    if channel.video_count > int(LIMIT):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many videos: {channel.video_count}. LIMIT: {LIMIT}",
        )
    page_token = None
    loop = True
    raw_videos: list[dict] = []
    while loop:
        playlist_response: dict = (
            api.playlistItems().list(
                part="snippet",
                maxResults=50,
                pageToken=page_token,
                playlistId=channel.upload_playlist_id,
            )
        ).execute()

        videos_response: dict = (
            api.videos()
            .list(
                part="snippet,statistics",
                id=[
                    v["snippet"]["resourceId"]["videoId"]
                    for v in playlist_response["items"]
                ],
            )
            .execute()
        )
        raw_videos.extend(videos_response["items"])

        page_token = playlist_response.get("nextPageToken")
        if page_token is None:
            loop = False

    def _find_thumbnail(thumbnail_obj: dict) -> tuple[str, int, int]:
        """Find the best thumbnail size."""
        keys = ["maxres", "standard", "high", "medium"]
        for k in keys:
            thumbnail = thumbnail_obj.get(k)
            if thumbnail is not None:
                return (
                    thumbnail["url"],
                    thumbnail["width"],
                    thumbnail["height"],
                )
        thumbnail = thumbnail_obj["default"]
        return (
            thumbnail["url"],
            thumbnail["width"],
            thumbnail["height"],
        )

    videos = []
    for v in raw_videos:
        thumbnail = _find_thumbnail(v["snippet"]["thumbnails"])
        video = Video(
            video_id=v["id"],
            published_at=v["snippet"]["publishedAt"],
            title=v["snippet"]["title"],
            view_count=v["statistics"]["viewCount"],
            like_count=v["statistics"]["likeCount"],
            thumbnail_url=thumbnail[0],
            thumbnail_width=thumbnail[1],
            thumbnail_height=thumbnail[2],
        )
        videos.append(video)

    return videos
