"""Root file."""
import json
import zipfile
from io import BytesIO

import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image

from app.models import Channel, Video, VideoList
from app.utils.decorators import check_handle
from app.youtube import get_channel_data, get_video_data

app = FastAPI()


@app.get("/")
async def root():
    """Root."""
    return {"message": "Welcome! Thumbnail Getter"}


@app.get("/search")
async def search_channels(query: str):
    """Search channels."""
    pass


@app.get("/channel", response_model=Channel)
@check_handle
async def get_channel(handle: str):
    """Obtain channel data."""

    return get_channel_data(handle)


@app.get("/videos", response_model=list[Video])
@check_handle
async def get_videos(handle: str):
    """Obtain video data."""

    channel = get_channel_data(handle)
    return get_video_data(channel)


@app.get("/thumbnails", response_class=StreamingResponse)
@check_handle
async def get_thumbnails(handle: str):
    """Download thumbnails."""

    channel: Channel = get_channel_data(handle)
    videos: list[Video] = get_video_data(channel)
    video_list: VideoList = VideoList(__root__=videos)

    def _get_thumbnail(url: str):
        with httpx.Client() as client:
            r = client.get(url)
            return r

    thumbnails: list[tuple[str, Image]] = []
    for v in videos:
        r = _get_thumbnail(v.thumbnail_url)
        img: Image = Image.open(BytesIO(r.content))
        fmt: str = v.thumbnail_url.split(".")[-1]
        thumbnails.append((f"{str(v)}.{fmt}", img))

    zip_buffer = BytesIO()
    with zipfile.ZipFile(
        zip_buffer, "w", compression=zipfile.ZIP_DEFLATED
    ) as z:
        for _filename, _img in thumbnails:

            # TODO: Fix this!
            pass
            # z.writestr(filename, img)
        z.mkdir("data")  # type: ignore
        with z.open("data/channel.json", "w") as f:
            f.write(
                json.dumps(
                    channel.json(), ensure_ascii=False, indent=2
                ).encode("utf-8")
            )
        with z.open("data/video.json", "w") as f:
            f.write(
                json.dumps(
                    video_list.json(), ensure_ascii=False, indent=2
                ).encode("utf-8")
            )
    zip_buffer.seek(0)
    response = StreamingResponse(zip_buffer, media_type="application/zip")
    response.headers[
        "Content-Disposition"
    ] = f'attachment; filename="{str(channel)}.zip"'
    return response
