"""Structured results the CheerLights tools return."""

from datetime import datetime

from pydantic import BaseModel, Field


class ColorChange(BaseModel):
    """One change of the CheerLights color."""

    color: str = Field(description="Color name, for example red")
    hex: str = Field(description="HEX value as published by CheerLights, for example #ff0000")
    set_at: datetime = Field(description="When the color was set (UTC)")
    entry_id: int = Field(description="ThingSpeak entry number of the change")


class ColorHistory(BaseModel):
    """Recent color changes, newest first."""

    changes: list[ColorChange] = Field(description="Color changes, newest first")
    count: int = Field(description="Number of changes returned")


class ColorStatistics(BaseModel):
    """How often each color was picked in a window of recent changes."""

    sample_size: int = Field(description="Number of recent changes analyzed")
    period_start: datetime | None = Field(description="Time of the oldest change analyzed (UTC)")
    period_end: datetime | None = Field(description="Time of the newest change analyzed (UTC)")
    counts: dict[str, int] = Field(description="Picks per color, most picked first")
    most_popular: str | None = Field(description="The color picked most often")
    least_popular: str | None = Field(description="The color picked least often")
    unique_colors: int = Field(description="Number of different colors picked")


class ColorSearchResult(BaseModel):
    """When a color was picked, newest first."""

    color: str = Field(description="The color searched for")
    searched: int = Field(description="Number of recent changes searched")
    matches: list[ColorChange] = Field(description="Changes to that color, newest first")
    match_count: int = Field(description="Number of matches returned")


class RGB(BaseModel):
    red: int = Field(ge=0, le=255)
    green: int = Field(ge=0, le=255)
    blue: int = Field(ge=0, le=255)


class PaletteColor(BaseModel):
    """A CheerLights color with its HEX and RGB values."""

    name: str = Field(description="Color name")
    hex: str = Field(description="HEX value, for example #ff0000")
    rgb: RGB = Field(description="RGB values, 0 to 255")
