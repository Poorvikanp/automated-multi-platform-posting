from app.platforms.base import Platform, PostError
from app.platforms.bluesky import Bluesky
from app.platforms.devto import DevTo
from app.platforms.github_gist import GitHubGist
from app.platforms.mastodon import Mastodon
from app.platforms.telegram import Telegram

__all__ = ["Platform", "PostError", "Mastodon", "default_platforms"]


def default_platforms():
    """Platform selection is handled internally; the API caller never picks."""
    return [Mastodon(), Bluesky(), DevTo(), GitHubGist(), Telegram()]
