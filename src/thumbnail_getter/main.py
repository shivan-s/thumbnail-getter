"""Main file."""

import json
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image
from pydantic import BaseModel
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from slugify import slugify

from utils import connect_api, logger

console = Console()
api = connect_api()

BASE_DIR = Path(__file__).parent.parent.parent
MEDIA = BASE_DIR / "media"
DEFAULT_Q = "RoxCodes"


class Channel(BaseModel):
    """YouTube Channel model."""

    channel_id: str
    title: str
    description: str
    upload_playlist_id: str | None
    video_count: int | None
    subscriber_count: int | None

    def __str__(self) -> str:
        """Represent string."""
        return f"{self.title}"

    @property
    def filename(self) -> str:
        """Filename."""
        return f"{self.title}-{self.channel_id[:4]}"


class Video(BaseModel):
    """Youtube video model."""

    video_id: str
    published_at: datetime
    title: str
    view_count: int
    like_count: int
    thumbnail_url: str | None
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
        return f"{slugify(self.title)}-{self.video_id[:4]}.{self.fileformat}"


class VideoList(BaseModel):
    """Video list / playlist."""

    __root__: list[Video]


def query_channel() -> Channel:
    """Query a channel.

    A query via search has to be done since we need the channel ID. \
            At the moment, the API does not allow lookup using handles. Plus \
            it's hard to determine what the channel ID is by browsing channels.

    Returns:
        type(Channel): Channel object that has been selected.
    """
    while True:
        q: str = Prompt.ask(
            ":video_camera: Please enter a channel username",
            default=DEFAULT_Q,
        )
        with console.status("Searching...", spinner="monkey"):
            search_result: dict = (
                api.search()
                .list(
                    part="snippet",
                    q=q,
                    type="channel",
                    maxResults=10,
                )
                .execute()
            )
        console.print(f'Channels found for term: "{q}"')
        channels: list[tuple[int, Channel]] = []
        for i, channel in enumerate(search_result["items"]):
            c = Channel(
                channel_id=channel["snippet"]["channelId"],
                title=channel["snippet"]["channelTitle"],
                description=channel["snippet"]["description"],
            )
            channels.append((i, c))
            console.print(f"{i}. {str(c)}")
        select: str | int = IntPrompt.ask(
            "Select channel by number",
            choices=[str(c[0]) for c in channels],
            default="0",
        )
        selected_channel: Channel = channels[int(select)][1]

        with console.status(
            "Fetching more channel information...", spinner="moon"
        ):
            channel_data = (
                api.channels()
                .list(
                    part="contentDetails,statistics",
                    id=selected_channel.channel_id,
                )
                .execute()
            )
        selected_channel.subscriber_count = channel_data["items"][0][
            "statistics"
        ].get("subscriberCount")
        selected_channel.video_count = channel_data["items"][0]["statistics"][
            "videoCount"
        ]
        selected_channel.upload_playlist_id = channel_data["items"][0][
            "contentDetails"
        ]["relatedPlaylists"]["uploads"]
        console.print(
            f"[bold cyan]{selected_channel.title}"
            + " - "
            + "[underline]"
            + f"https://youtube.com/c/{selected_channel.channel_id}]"
            + "[/underline][/]"
        )
        console.print(f"[bold]ID[/]: {selected_channel.channel_id}")
        console.print(f"[bold]Videos[/]: {selected_channel.video_count}")
        console.print(
            f"[bold]Subscribers[/]: {selected_channel.subscriber_count}"
        )
        console.print(f"[bold]Description[/]: {selected_channel.description}")
        if Confirm.ask("Correct channel?", default="y"):
            return selected_channel


def get_videos(channel: Channel) -> VideoList:
    """Get videos data and download thumbnails from a channel.

    Args:
        channel (Channel): YouTube channel of interested.

    Returns:
        VideoList: List of video data.
    """

    page_token = None
    loop = True
    raw_videos: list[dict] = []
    while loop:
        console.status(f"Videos collected: {len(raw_videos)}", spinner="earth")
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

    def _get_thumbnail(url: str):
        with httpx.Client() as client:
            r = client.get(url)
            return r

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

        with console.status(
            f"Saving thumbnails for {video.title}...",
            spinner=f"dots{random.randint(2,12)}",
        ):
            r = _get_thumbnail(video.thumbnail_url)
            img = Image.open(BytesIO(r.content))
            fmt: str = video.thumbnail_url.split(".")[-1]
            FORMATS = {"jpg": "JPEG"}
            channel_fp = BASE_DIR / "media" / f"{channel.filename}"
            channel_fp.mkdir(exist_ok=True, parents=True)
            fp = (
                BASE_DIR
                / "media"
                / f"{channel.filename}"
                / f"{video.filename}"
            )
            img.save(fp=fp, format=FORMATS.get(fmt.lower()))

    return VideoList(__root__=videos)


def main():
    """Main."""
    logger.debug("*** API KEY WILL BE EXPOSED ***")
    channel: Channel = query_channel()
    videos: VideoList = get_videos(channel)

    fp = BASE_DIR / "media" / f"{channel.filename}" / "data"
    fp.mkdir(exist_ok=True)
    with open(fp / "channel.json", "w") as f:
        json.dump(channel.json(), f)
    with open(fp / "video.json", "w") as f:
        json.dump(videos.json(), f)


if __name__ == "__main__":
    main()
