"""Tests for CheerLights API client."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from cheerlights_mcp.api import ThingSpeakClient
from cheerlights_mcp.api.thingspeak import ThingSpeakError
from cheerlights_mcp.models import ColorData


@pytest.fixture
def mock_response_data():
    """Sample ThingSpeak API response data."""
    return {
        "channel": {
            "id": 1417,
            "name": "CheerLights",
            "description": "CheerLights Channel",
            "field1": "Color",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "last_entry_id": 12345
        },
        "feeds": [
            {
                "created_at": "2024-01-01T12:00:00Z",
                "entry_id": 12345,
                "field1": "red"
            },
            {
                "created_at": "2024-01-01T11:00:00Z",
                "entry_id": 12344,
                "field1": "blue"
            }
        ]
    }


class TestThingSpeakClient:
    """Tests for ThingSpeakClient."""
    
    def test_client_initialization(self):
        """Test client initialization with default values."""
        client = ThingSpeakClient()
        
        assert client.base_url == "https://api.thingspeak.com"
        assert client.channel_id == "1417"
        assert client.timeout == 10.0
        assert client._client is None
    
    def test_client_initialization_custom(self):
        """Test client initialization with custom values."""
        client = ThingSpeakClient(
            base_url="https://custom.api.com",
            channel_id="9999",
            timeout=30.0
        )
        
        assert client.base_url == "https://custom.api.com"
        assert client.channel_id == "9999"
        assert client.timeout == 30.0
    
    @pytest.mark.asyncio
    async def test_fetch_feeds_success(self, mock_response_data):
        """Test successful feed fetching."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_client.get.return_value = mock_response
            
            client = ThingSpeakClient()
            result = await client.fetch_feeds(results=2)
            
            assert result == mock_response_data
            mock_client.get.assert_called_once_with(
                "https://api.thingspeak.com/channels/1417/feeds.json",
                params={"results": 2}
            )
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_feeds_http_error(self):
        """Test fetch feeds with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            from httpx import HTTPStatusError, Request, Response
            mock_response = Response(404, request=Request("GET", "http://test"))
            mock_client.get.side_effect = HTTPStatusError(
                "Not found", request=mock_response.request, response=mock_response
            )
            
            client = ThingSpeakClient()
            
            with pytest.raises(ThingSpeakError) as exc_info:
                await client.fetch_feeds()
            
            assert "HTTP 404" in str(exc_info.value)
    
    @pytest.mark.asyncio 
    async def test_fetch_feeds_request_error(self):
        """Test fetch feeds with request error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            from httpx import RequestError, Request
            request = Request("GET", "http://test")
            mock_client.get.side_effect = RequestError("Connection failed", request=request)
            
            client = ThingSpeakClient()
            
            with pytest.raises(ThingSpeakError) as exc_info:
                await client.fetch_feeds()
            
            assert "Request failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_current_color_success(self, mock_response_data):
        """Test successful current color retrieval."""
        with patch.object(ThingSpeakClient, "fetch_feeds") as mock_fetch:
            mock_fetch.return_value = mock_response_data
            
            client = ThingSpeakClient()
            result = await client.get_current_color()
            
            assert isinstance(result, ColorData)
            assert result.color == "red"
            assert result.entry_id == "12345"
            mock_fetch.assert_called_once_with(results=1)
    
    @pytest.mark.asyncio
    async def test_get_current_color_no_data(self):
        """Test current color with no data."""
        with patch.object(ThingSpeakClient, "fetch_feeds") as mock_fetch:
            mock_fetch.return_value = {"feeds": []}
            
            client = ThingSpeakClient()
            result = await client.get_current_color()
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_color_history_success(self, mock_response_data):
        """Test successful color history retrieval."""
        with patch.object(ThingSpeakClient, "fetch_feeds") as mock_fetch:
            mock_fetch.return_value = mock_response_data
            
            client = ThingSpeakClient()
            result = await client.get_color_history(count=2)
            
            assert len(result) == 2
            assert all(isinstance(item, ColorData) for item in result)
            assert result[0].color == "red"
            assert result[1].color == "blue"
            mock_fetch.assert_called_once_with(results=2)
    
    @pytest.mark.asyncio
    async def test_get_color_history_empty(self):
        """Test color history with empty data."""
        with patch.object(ThingSpeakClient, "fetch_feeds") as mock_fetch:
            mock_fetch.return_value = None
            
            client = ThingSpeakClient()
            result = await client.get_color_history()
            
            assert result == []
    
    def test_parse_feed_to_color_data_success(self):
        """Test successful feed parsing."""
        client = ThingSpeakClient()
        feed = {
            "created_at": "2024-01-01T12:00:00Z",
            "entry_id": 12345,
            "field1": "red"
        }
        
        result = client._parse_feed_to_color_data(feed)
        
        assert result is not None
        assert result.color == "red"
        assert result.entry_id == "12345"
        assert "2024-01-01 12:00:00 UTC" in result.timestamp
    
    def test_parse_feed_to_color_data_invalid_timestamp(self):
        """Test feed parsing with invalid timestamp."""
        client = ThingSpeakClient()
        feed = {
            "created_at": "invalid-timestamp",
            "entry_id": 12345,
            "field1": "red"
        }
        
        result = client._parse_feed_to_color_data(feed)
        
        assert result is not None
        assert result.color == "red"
        assert result.timestamp == "invalid-timestamp"
    
    def test_parse_feed_to_color_data_missing_fields(self):
        """Test feed parsing with missing fields."""
        client = ThingSpeakClient()
        feed = {}  # Empty feed
        
        result = client._parse_feed_to_color_data(feed)
        
        assert result is not None
        assert result.color == "unknown"
        assert result.entry_id == "unknown"
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as async context manager."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            async with ThingSpeakClient() as client:
                assert client._client is mock_client
            
            mock_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close method."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            client = ThingSpeakClient()
            client._client = mock_client
            
            await client.close()
            
            mock_client.aclose.assert_called_once()
            assert client._client is None
    
    def test_results_limit_enforcement(self):
        """Test that results parameter limits are enforced."""
        client = ThingSpeakClient()
        
        # Test minimum limit
        with patch.object(client, "client") as mock_client:
            mock_response = AsyncMock()
            mock_client.get.return_value = mock_response
            
            # This should be adjusted to 1
            import asyncio
            asyncio.run(client.fetch_feeds(results=-5))
            
            mock_client.get.assert_called_with(
                "https://api.thingspeak.com/channels/1417/feeds.json",
                params={"results": 1}
            )
        
        # Test maximum limit
        with patch.object(client, "client") as mock_client:
            mock_response = AsyncMock()
            mock_client.get.return_value = mock_response
            
            # This should be adjusted to 8000
            asyncio.run(client.fetch_feeds(results=10000))
            
            mock_client.get.assert_called_with(
                "https://api.thingspeak.com/channels/1417/feeds.json",
                params={"results": 8000}
            )
