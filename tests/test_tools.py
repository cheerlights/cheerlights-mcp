"""Tests for CheerLights tools."""

import pytest
from unittest.mock import AsyncMock, patch

from cheerlights_mcp.tools.color_tools import (
    get_current_color,
    get_color_history,
    get_color_statistics,
    search_color_history,
    get_color_hex,
)
from cheerlights_mcp.models import ColorData, ColorHistory, ColorStatistics, ColorSearchResult, HexColor


@pytest.fixture
def mock_context():
    """Mock MCP context for testing."""
    context = AsyncMock()
    context.debug = AsyncMock()
    context.info = AsyncMock()
    context.warning = AsyncMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def sample_color_data():
    """Sample color data for testing."""
    return [
        ColorData(color="red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1"),
        ColorData(color="blue", timestamp="2024-01-01 11:00:00 UTC", entry_id="2"),
        ColorData(color="green", timestamp="2024-01-01 10:00:00 UTC", entry_id="3"),
        ColorData(color="red", timestamp="2024-01-01 09:00:00 UTC", entry_id="4"),
        ColorData(color="yellow", timestamp="2024-01-01 08:00:00 UTC", entry_id="5"),
    ]


class TestGetCurrentColor:
    """Tests for get_current_color tool."""
    
    @pytest.mark.asyncio
    async def test_get_current_color_success(self, mock_context, sample_color_data):
        """Test successful current color retrieval."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_current_color.return_value = sample_color_data[0]
            
            result = await get_current_color(mock_context)
            
            assert result == sample_color_data[0]
            mock_context.debug.assert_called_once()
            mock_context.info.assert_called_once_with("Current color: red")
    
    @pytest.mark.asyncio
    async def test_get_current_color_no_data(self, mock_context):
        """Test current color when no data available."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_current_color.return_value = None
            
            result = await get_current_color(mock_context)
            
            assert result.color == "unknown"
            mock_context.warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_color_error(self, mock_context):
        """Test current color with API error."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_current_color.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await get_current_color(mock_context)
            
            mock_context.error.assert_called_once()


class TestGetColorHistory:
    """Tests for get_color_history tool."""
    
    @pytest.mark.asyncio
    async def test_get_color_history_success(self, mock_context, sample_color_data):
        """Test successful color history retrieval."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data[:3]
            
            result = await get_color_history(mock_context, count=3)
            
            assert isinstance(result, ColorHistory)
            assert len(result.colors) == 3
            assert result.count == 3
            mock_context.info.assert_called_once_with("Retrieved 3 color entries")
    
    @pytest.mark.asyncio
    async def test_get_color_history_limit_enforcement(self, mock_context, sample_color_data):
        """Test that count limits are enforced."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data[:5]
            
            # Test minimum limit
            result = await get_color_history(mock_context, count=-5)
            mock_client.get_color_history.assert_called_with(count=1)
            
            # Test maximum limit
            result = await get_color_history(mock_context, count=200)
            mock_client.get_color_history.assert_called_with(count=100)
    
    @pytest.mark.asyncio
    async def test_get_color_history_empty(self, mock_context):
        """Test color history with no data."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = []
            
            result = await get_color_history(mock_context)
            
            assert isinstance(result, ColorHistory)
            assert len(result.colors) == 0
            assert result.count == 0
            mock_context.warning.assert_called_once()


class TestGetColorStatistics:
    """Tests for get_color_statistics tool."""
    
    @pytest.mark.asyncio
    async def test_get_color_statistics_success(self, mock_context, sample_color_data):
        """Test successful statistics calculation."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            result = await get_color_statistics(mock_context, sample_size=50)
            
            assert isinstance(result, ColorStatistics)
            assert result.color_counts["red"] == 2
            assert result.most_popular == "red"
            assert result.total_changes == 5
            assert result.unique_colors == 4
            mock_context.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_color_statistics_limit_enforcement(self, mock_context, sample_color_data):
        """Test that sample_size limits are enforced."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            # Test minimum limit
            await get_color_statistics(mock_context, sample_size=5)
            mock_client.get_color_history.assert_called_with(count=10)
            
            # Test maximum limit
            await get_color_statistics(mock_context, sample_size=1000)
            mock_client.get_color_history.assert_called_with(count=500)
    
    @pytest.mark.asyncio
    async def test_get_color_statistics_no_data(self, mock_context):
        """Test statistics with no data."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = []
            
            result = await get_color_statistics(mock_context)
            
            assert isinstance(result, ColorStatistics)
            assert result.total_changes == 0
            assert result.most_popular == "unknown"
            mock_context.warning.assert_called_once()


class TestSearchColorHistory:
    """Tests for search_color_history tool."""
    
    @pytest.mark.asyncio
    async def test_search_color_history_success(self, mock_context, sample_color_data):
        """Test successful color search."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            result = await search_color_history(mock_context, color="red", limit=20)
            
            assert isinstance(result, ColorSearchResult)
            assert result.query == "red"
            assert result.match_count == 2  # Two red entries in sample data
            assert len(result.matches) == 2
            mock_context.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_color_history_partial_match(self, mock_context, sample_color_data):
        """Test color search with partial matches."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            result = await search_color_history(mock_context, color="re", limit=20)
            
            assert isinstance(result, ColorSearchResult)
            assert result.query == "re"
            assert result.match_count == 2  # Should match "red" entries
    
    @pytest.mark.asyncio
    async def test_search_color_history_no_matches(self, mock_context, sample_color_data):
        """Test color search with no matches."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            result = await search_color_history(mock_context, color="purple", limit=20)
            
            assert isinstance(result, ColorSearchResult)
            assert result.query == "purple"
            assert result.match_count == 0
            assert len(result.matches) == 0
    
    @pytest.mark.asyncio
    async def test_search_color_history_limit_enforcement(self, mock_context, sample_color_data):
        """Test that search limits are enforced."""
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = sample_color_data
            
            # Test minimum limit
            result = await search_color_history(mock_context, color="red", limit=-5)
            # Should still work but with corrected limit
            
            # Test maximum limit
            result = await search_color_history(mock_context, color="red", limit=200)
            # Should still work but with corrected limit


class TestGetColorHex:
    """Tests for get_color_hex tool."""
    
    @pytest.mark.asyncio
    async def test_get_color_hex_success(self, mock_context):
        """Test successful hex color retrieval."""
        with patch("cheerlights_mcp.tools.color_tools.get_hex_color") as mock_get_hex:
            mock_hex_color = HexColor(
                color_name="red",
                hex_code="#FF0000",
                rgb={"red": 255, "green": 0, "blue": 0}
            )
            mock_get_hex.return_value = mock_hex_color
            
            result = await get_color_hex(mock_context, "red")
            
            assert result == mock_hex_color
            mock_context.info.assert_called_once_with("Found hex code for 'red': #FF0000")
    
    @pytest.mark.asyncio
    async def test_get_color_hex_not_found(self, mock_context):
        """Test hex color retrieval for unknown color."""
        with patch("cheerlights_mcp.tools.color_tools.get_hex_color") as mock_get_hex:
            mock_get_hex.return_value = None
            
            result = await get_color_hex(mock_context, "unknowncolor")
            
            assert result is None
            mock_context.warning.assert_called_once_with("No hex code found for color 'unknowncolor'")
    
    @pytest.mark.asyncio
    async def test_get_color_hex_error(self, mock_context):
        """Test hex color retrieval with error."""
        with patch("cheerlights_mcp.tools.color_tools.get_hex_color") as mock_get_hex:
            mock_get_hex.side_effect = Exception("Color mapping error")
            
            with pytest.raises(Exception):
                await get_color_hex(mock_context, "red")
            
            mock_context.error.assert_called_once()


class TestToolsIntegration:
    """Integration tests for tools working together."""
    
    @pytest.mark.asyncio
    async def test_tools_with_real_color_mapping(self, mock_context):
        """Test tools using real color mapping data."""
        # Test get_color_hex with real color mapping
        result = await get_color_hex(mock_context, "red")
        
        assert result is not None
        assert result.hex_code == "#FF0000"
        assert result.rgb["red"] == 255
    
    @pytest.mark.asyncio 
    async def test_case_insensitive_operations(self, mock_context, sample_color_data):
        """Test that tools handle case-insensitive color operations."""
        # Create sample data with mixed case
        mixed_case_data = [
            ColorData(color="Red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1"),
            ColorData(color="BLUE", timestamp="2024-01-01 11:00:00 UTC", entry_id="2"),
            ColorData(color="green", timestamp="2024-01-01 10:00:00 UTC", entry_id="3"),
        ]
        
        with patch("cheerlights_mcp.tools.color_tools.ThingSpeakClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_color_history.return_value = mixed_case_data
            
            # Test search is case insensitive
            result = await search_color_history(mock_context, color="RED", limit=20)
            assert result.match_count >= 1  # Should find "Red"
            
            # Test statistics are case insensitive
            stats_result = await get_color_statistics(mock_context, sample_size=10)
            # Should count all variations as the same color in statistics
            assert stats_result.unique_colors == 3
