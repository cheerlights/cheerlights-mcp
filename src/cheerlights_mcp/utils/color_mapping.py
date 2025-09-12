"""Color mapping utilities for CheerLights colors."""

from typing import Dict, Optional, Tuple

from ..models import HexColor

# CheerLights standard colors to hex mapping
COLOR_HEX_MAP: Dict[str, str] = {
    "red": "#FF0000",
    "green": "#008000",
    "blue": "#0000FF",
    "cyan": "#00FFFF",
    "white": "#FFFFFF",
    "warmwhite": "#FDF5E6",  # Old lace
    "purple": "#800080",
    "magenta": "#FF00FF",
    "yellow": "#FFFF00",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "oldlace": "#FDF5E6",
    "black": "#000000",
    # Alternative names/spellings
    "violet": "#800080",  # Same as purple
    "lime": "#00FF00",    # Bright green
}


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert hex color code to RGB values.
    
    Args:
        hex_code: Hex color code (with or without #)
    
    Returns:
        Tuple of (red, green, blue) values
    """
    hex_code = hex_code.lstrip("#")
    if len(hex_code) != 6:
        raise ValueError(f"Invalid hex code: {hex_code}")
    
    return (
        int(hex_code[0:2], 16),
        int(hex_code[2:4], 16),
        int(hex_code[4:6], 16)
    )


def get_hex_color(color_name: str) -> Optional[HexColor]:
    """Get hex color information for a CheerLights color.
    
    Args:
        color_name: The color name (case-insensitive)
    
    Returns:
        HexColor object with hex code and RGB values, or None if not found
    """
    color_lower = color_name.lower().strip()
    hex_code = COLOR_HEX_MAP.get(color_lower)
    
    if not hex_code:
        return None
    
    try:
        r, g, b = hex_to_rgb(hex_code)
        return HexColor(
            color_name=color_name,
            hex_code=hex_code,
            rgb={"red": r, "green": g, "blue": b}
        )
    except ValueError:
        return None


def normalize_color_name(color_name: str) -> str:
    """Normalize a color name to standard CheerLights format.
    
    Args:
        color_name: The color name to normalize
    
    Returns:
        Normalized color name
    """
    color_lower = color_name.lower().strip()
    
    # Handle common variations
    if color_lower in ["violet", "purple"]:
        return "purple"
    elif color_lower in ["lime", "lightgreen"]:
        return "green"
    elif color_lower in ["warmwhite", "warm white", "oldlace", "old lace"]:
        return "warmwhite"
    
    return color_lower


def get_all_supported_colors() -> Dict[str, HexColor]:
    """Get all supported CheerLights colors with their hex information.
    
    Returns:
        Dictionary mapping color names to HexColor objects
    """
    result = {}
    for color_name in COLOR_HEX_MAP:
        hex_color = get_hex_color(color_name)
        if hex_color:
            result[color_name] = hex_color
    return result
