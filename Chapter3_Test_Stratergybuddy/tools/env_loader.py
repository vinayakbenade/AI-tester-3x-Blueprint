"""Load environment variables from .env file in the project root."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOT_ENV = PROJECT_ROOT / ".env"


def load_env():
    if not DOT_ENV.exists():
        raise FileNotFoundError(f".env not found at {DOT_ENV}")
    for line in DOT_ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("\"'")
        if value:
            os.environ.setdefault(key, value)


def get_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise ValueError(f"Environment variable {key} is empty or not set in .env")
    return val
