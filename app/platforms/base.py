from abc import ABC, abstractmethod
from typing import Tuple

import httpx

from app.config import env


class PostError(Exception):
    """A platform-specific, human-readable failure."""


class Platform(ABC):
    name: str = "base"
    required_env: Tuple[str, ...] = ()

    def missing_credentials(self):
        return [key for key in self.required_env if not env(key)]

    @abstractmethod
    async def publish(self, message: str, client: httpx.AsyncClient) -> str:
        """Publish the message and return the public URL of the post."""

    @staticmethod
    def check(response: httpx.Response, what: str) -> dict:
        """Raise PostError with a useful message unless the response is 2xx JSON."""
        if response.status_code in (401, 403):
            raise PostError(f"Authentication failed ({response.status_code}) at {what}")
        if response.status_code == 429:
            raise PostError(f"Rate limited (429) at {what}")
        if not response.is_success:
            raise PostError(f"{what} returned {response.status_code}: {response.text[:200]}")
        try:
            return response.json()
        except ValueError:
            raise PostError(f"{what} returned a non-JSON response")
