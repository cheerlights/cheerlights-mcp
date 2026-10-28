"""Reads the CheerLights color history from ThingSpeak channel 1417."""

import logging
from datetime import datetime
from types import TracebackType

import httpx

from .models import ColorChange

logger = logging.getLogger(__name__)

BASE_URL = "https://api.thingspeak.com"
CHANNEL = "1417"
MAX_RESULTS = 8000  # the most entries ThingSpeak returns in one request


class ThingSpeakError(Exception):
    """The CheerLights feed could not be read."""


class ThingSpeakClient:
    """Async client for the CheerLights channel. Use it as an async context manager."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        channel: str = CHANNEL,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=transport)
        self._path = f"/channels/{channel}/feeds.json"

    async def __aenter__(self) -> "ThingSpeakClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._http.aclose()

    async def recent_changes(self, count: int) -> list[ColorChange]:
        """The last `count` color changes, newest first."""
        count = max(1, min(count, MAX_RESULTS))
        try:
            response = await self._http.get(self._path, params={"results": count})
            response.raise_for_status()
            feeds = response.json().get("feeds") or []
        except httpx.HTTPStatusError as e:
            raise ThingSpeakError(f"ThingSpeak answered HTTP {e.response.status_code}") from e
        except (httpx.RequestError, ValueError) as e:
            raise ThingSpeakError(f"ThingSpeak could not be reached: {e}") from e

        changes = []
        for feed in reversed(feeds):  # ThingSpeak returns oldest first
            change = _parse(feed)
            if change is not None:
                changes.append(change)
        return changes

    async def current(self) -> ColorChange:
        """The current color."""
        changes = await self.recent_changes(1)
        if not changes:
            raise ThingSpeakError("ThingSpeak returned no color")
        return changes[0]


def _parse(feed: dict[str, object]) -> ColorChange | None:
    """One ThingSpeak feed entry as a ColorChange, or None if it is incomplete."""
    color, hex_code, created, entry = (
        feed.get("field1"),
        feed.get("field2"),
        feed.get("created_at"),
        feed.get("entry_id"),
    )
    if not isinstance(color, str) or not isinstance(created, str) or entry is None:
        logger.warning("skipping incomplete feed entry %s", feed)
        return None
    return ColorChange(
        color=color.strip().lower(),
        hex=hex_code.strip().lower() if isinstance(hex_code, str) else "",
        set_at=datetime.fromisoformat(created.replace("Z", "+00:00")),
        entry_id=int(str(entry)),
    )
