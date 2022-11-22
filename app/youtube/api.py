"""Connecting with the Google API for YouTube."""
import os

import googleapiclient.discovery
import googleapiclient.errors

from app.utils.logging import logger


def _connect_api() -> type[googleapiclient.discovery.Resource]:
    """Connect with YouTube API."""
    api_service_name = "youtube"
    api_version = "v3"
    api_key = os.getenv("YT_API_KEY", None)
    if api_key is None:
        logger.warn("KEY NOT SET")
    try:
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=api_key
        )
    except Exception:
        logger.error("Error on creating API", exc_info=True)
    return youtube


api = _connect_api()
