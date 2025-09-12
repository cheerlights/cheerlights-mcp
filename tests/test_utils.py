"""Tests for CheerLights utilities."""

import pytest
from datetime import datetime

from cheerlights_mcp.utils.color_mapping import (
    COLOR_HEX_MAP,
    hex_to_rgb,
    get_hex_color,
    normalize_color_name,
    get_all_supported_colors,
)
from cheerlights_mcp.utils.statistics import (
    calculate_color_statistics,
    find_color_transitions,
    get_color_duration_stats,
)
from cheerlights_mcp.models import ColorData, HexColor


class TestColorMapping:
    """Tests for color mapping utilities."""
    
    def test_color_hex_map_contains_standard_colors(self):
        """Test that COLOR_HEX_MAP contains standard CheerLights colors."""
        expected_colors = ["red", "green", "blue", "cyan", "white", "purple", "yellow", "orange"]
        
        for color in expected_colors:
            assert color in COLOR_HEX_MAP
            assert COLOR_HEX_MAP[color].startswith("#")
            assert len(COLOR_HEX_MAP[color]) == 7  # #RRGGBB format
    
    def test_hex_to_rgb_valid(self):
        """Test hex to RGB conversion with valid inputs."""
        # Test with #
        r, g, b = hex_to_rgb("#FF0000")
        assert (r, g, b) == (255, 0, 0)
        
        # Test without #
        r, g, b = hex_to_rgb("00FF00")
        assert (r, g, b) == (0, 255, 0)
        
        # Test blue
        r, g, b = hex_to_rgb("#0000FF")
        assert (r, g, b) == (0, 0, 255)
    
    def test_hex_to_rgb_invalid(self):
        """Test hex to RGB conversion with invalid inputs."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FF00")  # Too short
        
        with pytest.raises(ValueError):
            hex_to_rgb("#FF00FF00")  # Too long
        
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")  # Invalid hex characters
    
    def test_get_hex_color_valid(self):
        """Test getting hex color for valid color names."""
        red_color = get_hex_color("red")
        
        assert red_color is not None
        assert isinstance(red_color, HexColor)
        assert red_color.color_name == "red"
        assert red_color.hex_code == "#FF0000"
        assert red_color.rgb["red"] == 255
        assert red_color.rgb["green"] == 0
        assert red_color.rgb["blue"] == 0
    
    def test_get_hex_color_case_insensitive(self):
        """Test that get_hex_color is case insensitive."""
        red_upper = get_hex_color("RED")
        red_lower = get_hex_color("red")
        red_mixed = get_hex_color("Red")
        
        assert red_upper is not None
        assert red_lower is not None
        assert red_mixed is not None
        assert red_upper.hex_code == red_lower.hex_code == red_mixed.hex_code
    
    def test_get_hex_color_invalid(self):
        """Test getting hex color for invalid color name."""
        result = get_hex_color("nonexistent")
        assert result is None
    
    def test_normalize_color_name(self):
        """Test color name normalization."""
        assert normalize_color_name("RED") == "red"
        assert normalize_color_name("  Blue  ") == "blue"
        assert normalize_color_name("violet") == "purple"
        assert normalize_color_name("VIOLET") == "purple"
        assert normalize_color_name("lime") == "green"
        assert normalize_color_name("warm white") == "warmwhite"
    
    def test_get_all_supported_colors(self):
        """Test getting all supported colors."""
        colors = get_all_supported_colors()
        
        assert isinstance(colors, dict)
        assert len(colors) > 0
        assert "red" in colors
        assert isinstance(colors["red"], HexColor)
        
        # Check that all colors have valid hex codes
        for color_name, hex_color in colors.items():
            assert hex_color.hex_code.startswith("#")
            assert len(hex_color.hex_code) == 7


class TestStatistics:
    """Tests for statistics utilities."""
    
    @pytest.fixture
    def sample_colors(self):
        """Sample color data for testing."""
        return [
            ColorData(color="red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1",
                     created_at=datetime(2024, 1, 1, 12, 0, 0)),
            ColorData(color="red", timestamp="2024-01-01 11:00:00 UTC", entry_id="2",
                     created_at=datetime(2024, 1, 1, 11, 0, 0)),
            ColorData(color="blue", timestamp="2024-01-01 10:00:00 UTC", entry_id="3",
                     created_at=datetime(2024, 1, 1, 10, 0, 0)),
            ColorData(color="green", timestamp="2024-01-01 09:00:00 UTC", entry_id="4",
                     created_at=datetime(2024, 1, 1, 9, 0, 0)),
            ColorData(color="red", timestamp="2024-01-01 08:00:00 UTC", entry_id="5",
                     created_at=datetime(2024, 1, 1, 8, 0, 0)),
        ]
    
    def test_calculate_color_statistics_empty(self):
        """Test calculating statistics with empty data."""
        stats = calculate_color_statistics([])
        
        assert stats.color_counts == {}
        assert stats.most_popular == "unknown"
        assert stats.least_popular == "unknown"
        assert stats.total_changes == 0
        assert stats.unique_colors == 0
        assert stats.analysis_period == "No data"
    
    def test_calculate_color_statistics_with_data(self, sample_colors):
        """Test calculating statistics with sample data."""
        stats = calculate_color_statistics(sample_colors)
        
        assert stats.color_counts["red"] == 3
        assert stats.color_counts["blue"] == 1
        assert stats.color_counts["green"] == 1
        assert stats.most_popular == "red"
        assert stats.least_popular in ["blue", "green"]  # Both have count 1
        assert stats.total_changes == 5
        assert stats.unique_colors == 3
    
    def test_find_color_transitions_empty(self):
        """Test finding transitions with empty data."""
        transitions = find_color_transitions([])
        assert transitions == []
    
    def test_find_color_transitions_single_color(self, sample_colors):
        """Test finding transitions with single color."""
        single_color = [sample_colors[0]]  # Just red
        transitions = find_color_transitions(single_color)
        assert transitions == []
    
    def test_find_color_transitions_with_changes(self, sample_colors):
        """Test finding transitions with color changes."""
        transitions = find_color_transitions(sample_colors)
        
        # Should find transitions between different colors
        assert len(transitions) > 0
        
        # Check transition format (from_color, to_color, timestamp)
        for transition in transitions:
            assert len(transition) == 3
            assert isinstance(transition[0], str)  # from_color
            assert isinstance(transition[1], str)  # to_color
            assert isinstance(transition[2], str)  # timestamp
    
    def test_get_color_duration_stats_empty(self):
        """Test duration stats with empty data."""
        stats = get_color_duration_stats([])
        assert stats == {}
    
    def test_get_color_duration_stats_insufficient_data(self, sample_colors):
        """Test duration stats with insufficient data."""
        stats = get_color_duration_stats([sample_colors[0]])
        assert stats == {}
    
    def test_get_color_duration_stats_with_data(self, sample_colors):
        """Test duration stats with sample data."""
        # Reverse order to simulate chronological order (oldest first)
        reversed_colors = list(reversed(sample_colors))
        stats = get_color_duration_stats(reversed_colors)
        
        # Should have duration data for colors that had transitions
        assert isinstance(stats, dict)
        
        # Check structure of returned data
        for color_name, duration_info in stats.items():
            assert "average_seconds" in duration_info
            assert "average_minutes" in duration_info
            assert "occurrences" in duration_info
            assert "total_seconds" in duration_info
            
            assert duration_info["average_seconds"] >= 0
            assert duration_info["average_minutes"] >= 0
            assert duration_info["occurrences"] > 0
            assert duration_info["total_seconds"] >= 0
    
    def test_analysis_period_determination(self, sample_colors):
        """Test analysis period determination with various time ranges."""
        # Test with colors that have datetime objects
        stats = calculate_color_statistics(sample_colors)
        
        # Should determine some time period
        assert stats.analysis_period != "No data"
        assert "hours" in stats.analysis_period or "minutes" in stats.analysis_period
    
    def test_case_insensitive_color_counting(self):
        """Test that color counting is case insensitive."""
        mixed_case_colors = [
            ColorData(color="Red", timestamp="2024-01-01 12:00:00 UTC", entry_id="1"),
            ColorData(color="RED", timestamp="2024-01-01 11:00:00 UTC", entry_id="2"),
            ColorData(color="red", timestamp="2024-01-01 10:00:00 UTC", entry_id="3"),
        ]
        
        stats = calculate_color_statistics(mixed_case_colors)
        
        assert stats.color_counts["red"] == 3
        assert stats.most_popular == "red"
        assert stats.unique_colors == 1
