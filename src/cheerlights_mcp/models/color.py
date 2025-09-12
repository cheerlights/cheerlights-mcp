"""Pydantic models for CheerLights color data."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ColorData(BaseModel):
    """Represents a single CheerLights color entry."""
    
    color: str = Field(..., description="The color name")
    timestamp: str = Field(..., description="When the color was set")
    entry_id: str = Field(..., description="Unique entry identifier")
    created_at: Optional[datetime] = Field(None, description="Parsed datetime object")


class ColorHistory(BaseModel):
    """Represents a collection of color history entries."""
    
    colors: List[ColorData] = Field(..., description="List of color entries")
    count: int = Field(..., description="Number of entries returned")
    total_available: Optional[int] = Field(None, description="Total entries available")


class ColorStatistics(BaseModel):
    """Statistics about CheerLights colors."""
    
    color_counts: Dict[str, int] = Field(..., description="Count of each color")
    most_popular: str = Field(..., description="Most frequently used color")
    least_popular: str = Field(..., description="Least frequently used color")
    total_changes: int = Field(..., description="Total number of color changes")
    unique_colors: int = Field(..., description="Number of unique colors used")
    analysis_period: str = Field(..., description="Time period analyzed")


class ColorSearchResult(BaseModel):
    """Result of searching for specific colors in history."""
    
    query: str = Field(..., description="The search query")
    matches: List[ColorData] = Field(..., description="Matching color entries")
    match_count: int = Field(..., description="Number of matches found")


class HexColor(BaseModel):
    """Hex color code information."""
    
    color_name: str = Field(..., description="The color name")
    hex_code: str = Field(..., description="Hex color code (e.g., #FF0000)")
    rgb: Dict[str, int] = Field(..., description="RGB values")
