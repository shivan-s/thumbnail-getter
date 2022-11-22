"""Custom decorators."""

from functools import wraps

import httpx
from fastapi import HTTPException, status

from app.utils.defaults import YOUTUBE_URL

from .validators import parse_handle


def check_handle(func):
    """Decorator to check if handle is valid."""

    @wraps(func)
    async def _wrapper(handle: str, *args, **kwargs):
        "Wrapper."
        handle = parse_handle(handle)
        r = httpx.get(f"{YOUTUBE_URL}{handle}")
        if r.status_code == status.HTTP_200_OK:
            result = await func(handle, *args, **kwargs)
        elif r.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{handle}' cannot be found",
            )
        return result

    return _wrapper
