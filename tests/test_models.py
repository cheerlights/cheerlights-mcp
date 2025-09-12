"""Tests for CheerLights data models."""

import pytest
from datetime import datetime

from cheerlights_mcp.models import ColorData, ColorHistory, ColorStatistics, ColorSearchResult, HexColor


class TestColorData:
    """Tests for ColorData model."""
    
    def test_color_data_creation(self):
        """Test creating a ColorData instance."""
        color_data = ColorData(
            color="red",
            timestamp="2024-01-01 12:00:00 UTC",
            entry_id="12345"
        )
        
        assert color_data.color == "red"
        assert color_data.timestamp == "2024-01-01 12:00:00 UTC"
        assert color_data.entry_id == "12345"
        assert color_data.created_at is None
    
    def test_color_data_with_datetime(self):
        """Test ColorData with datetime object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        color_data = ColorData(
            color="blue",
            timestamp="2024-01-01 12:00:00 UTC",
            entry_id="12345",
            created_at=dt
        )
        
        assert color_data.created_at == dt
    
    def test_color_data_validation(self):
        """Test ColorData field validation."""
        with pytest.raises(ValueError):
            ColorData()  # Missing required fields


class TestColorHistory:
    """Tests for ColorHistory model."""
    
    def test_empty_history(self):
        """Test creating empty color history."""
        history = ColorHistory(colors=[], count=0)
        
        assert history.colors == []
        assert history.count == 0
        assert history.total_available is None
    
    def test_history_with_colors(self):
        """Test color history with data."""
        colors = [
            ColorData(color="red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1"),
            ColorData(color="blue", timestamp="2024-01-01 11:00:00 UTC", entry_id="2"),
        ]
        
        history = ColorHistory(colors=colors, count=2, total_available=100)
        
        assert len(history.colors) == 2
        assert history.count == 2
        assert history.total_available == 100


class TestColorStatistics:
    """Tests for ColorStatistics model."""
    
    def test_statistics_creation(self):
        """Test creating color statistics."""
        stats = ColorStatistics(
            color_counts={"red": 5, "blue": 3, "green": 2},
            most_popular="red",
            least_popular="green",
            total_changes=10,
            unique_colors=3,
            analysis_period="1 hour"
        )
        
        assert stats.color_counts["red"] == 5
        assert stats.most_popular == "red"
        assert stats.least_popular == "green"
        assert stats.total_changes == 10
        assert stats.unique_colors == 3


class TestColorSearchResult:
    """Tests for ColorSearchResult model."""
    
    def test_search_result(self):
        """Test color search result."""
        matches = [
            ColorData(color="red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1"),
        ]
        
        result = ColorSearchResult(
            query="red",
            matches=matches,
            match_count=1
        )
        
        assert result.query == "red"
        assert len(result.matches) == 1
        assert result.match_count == 1


class TestHexColor:
    """Tests for HexColor model."""
    
    def test_hex_color_creation(self):
        """Test creating hex color."""
        hex_color = HexColor(
            color_name="red",
            hex_code="#FF0000",
            rgb={"red": 255, "green": 0, "blue": 0}
        )
        
        assert hex_color.color_name == "red"
        assert hex_color.hex_code == "#FF0000"
        assert hex_color.rgb["red"] == 255
        assert hex_color.rgb["green"] == 0
        assert hex_color.rgb["blue"] == 0
