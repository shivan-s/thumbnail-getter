"""Root file."""
import asyncio
import json
import zipfile
from io import BytesIO

import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.models import Channel, Video, VideoList
from app.utils.decorators import check_handle
from app.youtube import get_channel_data, get_video_data

app = FastAPI()


@app.get("/")
async def root():
    """Root."""
    return {"message": "Welcome! Thumbnail Getter"}


@app.get("/channel", response_model=Channel)
@check_handle
async def get_channel(handle: str):
    """Obtain channel data given a handle.

    Example:
        `/channel?handle=RoxCodes`
    """
    return get_channel_data(handle)


@app.get("/videos", response_model=list[Video])
@check_handle
async def get_videos(handle: str):
    """Obtain video data given a handle.

    Example:
        `/videos?handle=RoxCodes`
    """

    channel = get_channel_data(handle)
    return get_video_data(channel)


@app.get("/thumbnails", response_class=StreamingResponse)
@check_handle
async def get_thumbnails(handle: str):
    """Download thumbnails as a zip file.

    Also, comes bundled with channel and video data stored in:
        - `data/channel.json`, and
        - `data/videos.json`.

    The schema for these `.json` files resembles the `/videos` and `/channel` \
            endpoints.
    Example:
        `/thumbnails?handle=RoxCodes`
    """

    channel: Channel = get_channel_data(handle)
    videos: list[Video] = get_video_data(channel)
    video_list: VideoList = VideoList(__root__=videos)

    zip_buff = BytesIO()
    with zipfile.ZipFile(zip_buff, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.mkdir("data")  # type: ignore
        with z.open("data/channel.json", "w") as f:
            f.write(
                json.dumps(
                    channel.json(), ensure_ascii=False, indent=4
                ).encode("utf-8")
            )
        with z.open("data/video.json", "w") as f:
            f.write(
                json.dumps(
                    video_list.json(), ensure_ascii=False, indent=4
                ).encode("utf-8")
            )

        async def _get_thumbnail(client: httpx.AsyncClient, video: Video):
            """Access a single thumbnail."""
            r = await client.get(video.thumbnail_url)
            buf = BytesIO(r.content)
            fmt: str = video.thumbnail_url.split(".")[-1]
            z.writestr(f"{video.filename}.{fmt}", buf.read())

        client = httpx.AsyncClient()
        tasks = []
        for v in videos:
            tasks.append(asyncio.create_task(_get_thumbnail(client, video=v)))
        await asyncio.gather(*tasks)
        await client.aclose()

    zip_buff.seek(0)
    response = StreamingResponse(zip_buff, media_type="application/zip")
    response.headers[
        "Content-Disposition"
    ] = f'attachment; filename="{channel.filename}.zip"'
    return response
