"""CheerLights color tools for MCP server."""

import logging
from typing import List, Optional

from mcp.server.fastmcp import Context

from ..api import ThingSpeakClient
from ..models import ColorData, ColorHistory, ColorStatistics, ColorSearchResult, HexColor
from ..utils import calculate_color_statistics, get_hex_color

logger = logging.getLogger(__name__)


async def get_current_color(ctx: Context) -> ColorData:
    """Get the most recent CheerLights color.
    
    Returns:
        ColorData with current color information
    """
    await ctx.debug("Fetching current CheerLights color")
    
    async with ThingSpeakClient() as client:
        try:
            current_color = await client.get_current_color()
            if not current_color:
                await ctx.warning("No current color data available")
                # Return a default response
                return ColorData(
                    color="unknown",
                    timestamp="unknown",
                    entry_id="unknown"
                )
            
            await ctx.info(f"Current color: {current_color.color}")
            return current_color
            
        except Exception as e:
            await ctx.error(f"Error fetching current color: {e}")
            raise


async def get_color_history(ctx: Context, count: int = 5) -> ColorHistory:
    """Get a history of recent CheerLights colors.
    
    Args:
        count: Number of colors to return (default: 5, max: 100)
    
    Returns:
        ColorHistory with recent color changes
    """
    # Enforce reasonable limits
    if count < 1:
        count = 1
    if count > 100:
        count = 100
        
    await ctx.debug(f"Fetching {count} colors from CheerLights history")
    
    async with ThingSpeakClient() as client:
        try:
            colors = await client.get_color_history(count=count)
            
            if not colors:
                await ctx.warning("No color history data available")
                return ColorHistory(colors=[], count=0)
            
            await ctx.info(f"Retrieved {len(colors)} color entries")
            
            return ColorHistory(
                colors=colors,
                count=len(colors),
                total_available=None  # ThingSpeak doesn't provide total count
            )
            
        except Exception as e:
            await ctx.error(f"Error fetching color history: {e}")
            raise


async def get_color_statistics(ctx: Context, sample_size: int = 50) -> ColorStatistics:
    """Get statistics about CheerLights color usage.
    
    Args:
        sample_size: Number of recent entries to analyze (default: 50, max: 500)
    
    Returns:
        ColorStatistics with analysis of color usage
    """
    # Enforce reasonable limits
    if sample_size < 10:
        sample_size = 10
    if sample_size > 500:
        sample_size = 500
    
    await ctx.debug(f"Analyzing {sample_size} recent colors for statistics")
    
    async with ThingSpeakClient() as client:
        try:
            colors = await client.get_color_history(count=sample_size)
            
            if not colors:
                await ctx.warning("No color data available for statistics")
                return ColorStatistics(
                    color_counts={},
                    most_popular="unknown",
                    least_popular="unknown", 
                    total_changes=0,
                    unique_colors=0,
                    analysis_period="No data"
                )
            
            stats = calculate_color_statistics(colors)
            await ctx.info(f"Calculated statistics for {len(colors)} colors")
            
            return stats
            
        except Exception as e:
            await ctx.error(f"Error calculating color statistics: {e}")
            raise


async def search_color_history(
    ctx: Context, 
    color: str, 
    limit: int = 20
) -> ColorSearchResult:
    """Search for specific colors in CheerLights history.
    
    Args:
        color: Color name to search for (case-insensitive)
        limit: Maximum number of results to return (default: 20, max: 100)
    
    Returns:
        ColorSearchResult with matching entries
    """
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    
    color_query = color.lower().strip()
    await ctx.debug(f"Searching for color '{color_query}' with limit {limit}")
    
    # To find matches, we need to get a larger sample and filter
    search_sample_size = min(limit * 10, 1000)  # Get more data to search through
    
    async with ThingSpeakClient() as client:
        try:
            all_colors = await client.get_color_history(count=search_sample_size)
            
            if not all_colors:
                await ctx.warning("No color data available for search")
                return ColorSearchResult(
                    query=color,
                    matches=[],
                    match_count=0
                )
            
            # Filter colors that match the search query
            matches = []
            for color_data in all_colors:
                if color_query in color_data.color.lower():
                    matches.append(color_data)
                    if len(matches) >= limit:
                        break
            
            await ctx.info(f"Found {len(matches)} matches for '{color}'")
            
            return ColorSearchResult(
                query=color,
                matches=matches,
                match_count=len(matches)
            )
            
        except Exception as e:
            await ctx.error(f"Error searching color history: {e}")
            raise


async def get_color_hex(ctx: Context, color_name: str) -> Optional[HexColor]:
    """Get hex color code and RGB values for a CheerLights color.
    
    Args:
        color_name: Name of the color to get hex code for
    
    Returns:
        HexColor with hex code and RGB values, or None if not found
    """
    await ctx.debug(f"Looking up hex code for color '{color_name}'")
    
    try:
        hex_color = get_hex_color(color_name)
        
        if hex_color:
            await ctx.info(f"Found hex code for '{color_name}': {hex_color.hex_code}")
        else:
            await ctx.warning(f"No hex code found for color '{color_name}'")
        
        return hex_color
        
    except Exception as e:
        await ctx.error(f"Error getting hex color: {e}")
        raise
