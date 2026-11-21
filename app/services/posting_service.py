import asyncio
import logging
from datetime import datetime
from typing import List

import httpx

from app.config import PLATFORM_TIMEOUT_SECONDS, REQUEST_TIMEOUT_SECONDS
from app.platforms.base import Platform, PostError
from app.schemas import PlatformResult

logger = logging.getLogger("posting")


def _failed(name: str, error: str) -> PlatformResult:
    return PlatformResult(platform=name, status="failed", public_access=False, error=error)


async def check_public_access(client: httpx.AsyncClient, url: str) -> bool:
    """Fetch the post anonymously (no auth headers) to confirm it is publicly visible."""
    try:
        resp = await client.get(url, follow_redirects=True, headers={"User-Agent": "posting-checker/1.0"})
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def _post_to_platform(platform: Platform, message: str, client: httpx.AsyncClient) -> PlatformResult:
    missing = platform.missing_credentials()
    if missing:
        return _failed(platform.name, f"Missing credentials: {', '.join(missing)}")
    try:
        url = await asyncio.wait_for(platform.publish(message, client), timeout=PLATFORM_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        return _failed(platform.name, f"Timed out after {PLATFORM_TIMEOUT_SECONDS}s")
    except PostError as exc:
        return _failed(platform.name, str(exc))
    except httpx.HTTPError as exc:
        return _failed(platform.name, f"Network error: {exc.__class__.__name__}: {exc}")
    except Exception as exc:  # one platform must never take down the others
        logger.exception("Unexpected error on %s", platform.name)
        return _failed(platform.name, f"Unexpected error: {exc.__class__.__name__}: {exc}")

    now = datetime.now()
    public = await check_public_access(client, url)
    return PlatformResult(
        platform=platform.name,
        status="success",
        posted_url=url,
        public_access=public,
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        error=None,
    )


async def post_to_all(message: str, platforms: List[Platform]) -> List[PlatformResult]:
    """Run every platform concurrently and independently; order matches `platforms`."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        return list(await asyncio.gather(*(_post_to_platform(p, message, client) for p in platforms)))
