"""ThingSpeak API client for CheerLights data."""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import ValidationError

from ..models import ColorData

logger = logging.getLogger(__name__)


class ThingSpeakError(Exception):
    """Base exception for ThingSpeak API errors."""
    pass


class ThingSpeakClient:
    """Client for interacting with ThingSpeak API for CheerLights data."""
    
    def __init__(
        self, 
        base_url: str = "https://api.thingspeak.com",
        channel_id: str = "1417",
        timeout: float = 10.0
    ) -> None:
        """Initialize ThingSpeak client.
        
        Args:
            base_url: ThingSpeak API base URL
            channel_id: CheerLights channel ID
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.channel_id = channel_id
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "ThingSpeakClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def fetch_feeds(self, results: int = 1) -> Optional[Dict[str, Any]]:
        """Fetch CheerLights data from ThingSpeak API.
        
        Args:
            results: Number of results to fetch (default: 1, max: 8000)
        
        Returns:
            Dictionary containing the API response or None if failed
            
        Raises:
            ThingSpeakError: If API request fails
        """
        if results < 1:
            results = 1
        elif results > 8000:  # ThingSpeak limit
            results = 8000
            
        url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
        params = {"results": results}
        
        try:
            logger.debug(f"Fetching {results} feed(s) from ThingSpeak API")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Successfully fetched {len(data.get('feeds', []))} feeds")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching ThingSpeak data: {e.response.status_code}")
            raise ThingSpeakError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching ThingSpeak data: {e}")
            raise ThingSpeakError(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching ThingSpeak data: {e}")
            raise ThingSpeakError(f"Unexpected error: {e}")
    
    async def get_current_color(self) -> Optional[ColorData]:
        """Get the most recent CheerLights color.
        
        Returns:
            ColorData object with current color info, or None if failed
        """
        data = await self.fetch_feeds(results=1)
        if not data or "feeds" not in data or not data["feeds"]:
            return None
        
        try:
            feed = data["feeds"][0]
            return self._parse_feed_to_color_data(feed)
        except (KeyError, IndexError, ValidationError) as e:
            logger.error(f"Error parsing current color data: {e}")
            return None
    
    async def get_color_history(self, count: int = 5) -> List[ColorData]:
        """Get a history of recent CheerLights colors.
        
        Args:
            count: Number of colors to return (default: 5, max: 8000)
        
        Returns:
            List of ColorData objects
        """
        data = await self.fetch_feeds(results=count)
        if not data or "feeds" not in data or not data["feeds"]:
            return []
        
        color_data = []
        for feed in data["feeds"]:
            try:
                color_entry = self._parse_feed_to_color_data(feed)
                if color_entry:
                    color_data.append(color_entry)
            except (KeyError, ValidationError) as e:
                logger.warning(f"Skipping invalid feed entry: {e}")
                continue
        
        return color_data
    
    def _parse_feed_to_color_data(self, feed: Dict[str, Any]) -> Optional[ColorData]:
        """Parse a ThingSpeak feed entry to ColorData.
        
        Args:
            feed: Raw feed data from ThingSpeak API
            
        Returns:
            ColorData object or None if parsing fails
        """
        try:
            # Field 1 contains the color name in the ThingSpeak channel
            color = feed.get("field1", "unknown")
            created_at = feed.get("created_at", "")
            entry_id = str(feed.get("entry_id", "unknown"))
            
            # Parse timestamp
            from dateutil.parser import parse as parse_date
            parsed_timestamp = None
            timestamp_str = created_at
            
            try:
                if created_at:
                    parsed_timestamp = parse_date(created_at)
                    timestamp_str = parsed_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            except Exception as e:
                logger.warning(f"Could not parse timestamp '{created_at}': {e}")
                timestamp_str = created_at or "unknown"
            
            return ColorData(
                color=color,
                timestamp=timestamp_str,
                entry_id=entry_id,
                created_at=parsed_timestamp
            )
            
        except Exception as e:
            logger.error(f"Error parsing feed to ColorData: {e}")
            return None
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
