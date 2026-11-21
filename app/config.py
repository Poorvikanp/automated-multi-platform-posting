import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

REQUEST_TIMEOUT_SECONDS = 15
PLATFORM_TIMEOUT_SECONDS = 25


def env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read an env var at call time; empty strings count as missing."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()
