import re
from typing import List, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_LENGTH = 200
_URL_CANDIDATE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_HOST_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)


def find_urls(text: str) -> List[str]:
    """Return link-like tokens, with trailing punctuation stripped."""
    return [u.rstrip(".,;:!?)\"'") for u in _URL_CANDIDATE.findall(text)]


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host or "." not in host:
        return False
    labels = host.split(".")
    return all(_HOST_LABEL.match(label) for label in labels) and len(labels[-1]) >= 2


class PostingRequest(BaseModel):
    message: str = Field(..., examples=["Check out our latest business platform and grow your online visibility. https://example.com"])

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message must not be empty.")
        if len(value) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message must not exceed {MAX_MESSAGE_LENGTH} characters (got {len(value)})."
            )
        urls = find_urls(value)
        if len(urls) != 1:
            raise ValueError(f"Message must contain exactly one CTA link (found {len(urls)}).")
        if not is_valid_url(urls[0]):
            raise ValueError(
                f"Invalid URL '{urls[0]}'. Use a full http:// or https:// link with a valid domain."
            )
        return value


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostingResponse(BaseModel):
    success: bool  # True if at least one platform succeeded
    results: List[PlatformResult]
