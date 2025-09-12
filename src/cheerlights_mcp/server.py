"""Main CheerLights MCP Server implementation."""

import logging
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .api import ThingSpeakClient
from .models import ColorData, ColorHistory, ColorStatistics, ColorSearchResult, HexColor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server(name: str = "CheerLights") -> FastMCP:
    """Create and configure the CheerLights MCP server.
    
    Args:
        name: Name for the MCP server
        
    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP(
        name=name,
        instructions="""
        CheerLights MCP Server - Connect to the global CheerLights network!
        
        CheerLights is a global IoT project that synchronizes colors across connected
        lights worldwide. This server provides access to the current color and
        historical data from the CheerLights API.
        
        Available capabilities:
        - Get the current CheerLights color
        - View color change history 
        - Analyze color usage statistics
        - Search for specific colors in history
        - Get hex color codes and RGB values
        - Access color history as a resource
        
        Use the tools to interact with live CheerLights data or browse the color
        history resource for context about recent changes.
        """.strip()
    )
    
    # Register tools with structured output
    @mcp.tool()
    async def get_current_cheerlights_color() -> ColorData:
        """Get the most recent CheerLights color from the global network."""
        async with ThingSpeakClient() as client:
            try:
                current_color = await client.get_current_color()
                if not current_color:
                    logger.warning("No current color data available")
                    return ColorData(
                        color="unknown",
                        timestamp="unknown", 
                        entry_id="unknown"
                    )
                
                logger.info(f"Current color: {current_color.color}")
                return current_color
                
            except Exception as e:
                logger.error(f"Error fetching current color: {e}")
                raise
    
    @mcp.tool()
    async def get_cheerlights_history(count: int = 5) -> ColorHistory:
        """Get a history of recent CheerLights color changes.
        
        Args:
            count: Number of recent colors to retrieve (1-100, default: 5)
        """
        # Enforce reasonable limits
        if count < 1:
            count = 1
        if count > 100:
            count = 100
            
        logger.debug(f"Fetching {count} colors from CheerLights history")
        
        async with ThingSpeakClient() as client:
            try:
                colors = await client.get_color_history(count=count)
                
                if not colors:
                    logger.warning("No color history data available")
                    return ColorHistory(colors=[], count=0)
                
                logger.info(f"Retrieved {len(colors)} color entries")
                
                return ColorHistory(
                    colors=colors,
                    count=len(colors),
                    total_available=None  # ThingSpeak doesn't provide total count
                )
                
            except Exception as e:
                logger.error(f"Error fetching color history: {e}")
                raise
    
    @mcp.tool()
    async def analyze_color_statistics(sample_size: int = 50) -> ColorStatistics:
        """Analyze CheerLights color usage statistics.
        
        Args:
            sample_size: Number of recent entries to analyze (10-500, default: 50)
        """
        from .utils.statistics import calculate_color_statistics
        
        # Enforce reasonable limits
        if sample_size < 10:
            sample_size = 10
        if sample_size > 500:
            sample_size = 500
        
        logger.debug(f"Analyzing {sample_size} recent colors for statistics")
        
        async with ThingSpeakClient() as client:
            try:
                colors = await client.get_color_history(count=sample_size)
                
                if not colors:
                    logger.warning("No color data available for statistics")
                    return ColorStatistics(
                        color_counts={},
                        most_popular="unknown",
                        least_popular="unknown", 
                        total_changes=0,
                        unique_colors=0,
                        analysis_period="No data"
                    )
                
                stats = calculate_color_statistics(colors)
                logger.info(f"Calculated statistics for {len(colors)} colors")
                
                return stats
                
            except Exception as e:
                logger.error(f"Error calculating color statistics: {e}")
                raise
    
    @mcp.tool()
    async def search_colors(color: str, limit: int = 20) -> ColorSearchResult:
        """Search for specific colors in CheerLights history.
        
        Args:
            color: Color name to search for (case-insensitive)
            limit: Maximum results to return (1-100, default: 20)
        """
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        
        color_query = color.lower().strip()
        logger.debug(f"Searching for color '{color_query}' with limit {limit}")
        
        # To find matches, we need to get a larger sample and filter
        search_sample_size = min(limit * 10, 1000)  # Get more data to search through
        
        async with ThingSpeakClient() as client:
            try:
                all_colors = await client.get_color_history(count=search_sample_size)
                
                if not all_colors:
                    logger.warning("No color data available for search")
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
                
                logger.info(f"Found {len(matches)} matches for '{color}'")
                
                return ColorSearchResult(
                    query=color,
                    matches=matches,
                    match_count=len(matches)
                )
                
            except Exception as e:
                logger.error(f"Error searching color history: {e}")
                raise
    
    @mcp.tool()
    async def get_hex_color_code(color_name: str) -> Optional[HexColor]:
        """Get hex color code and RGB values for a CheerLights color.
        
        Args:
            color_name: Name of the CheerLights color
        """
        from .utils.color_mapping import get_hex_color
        
        logger.debug(f"Looking up hex code for color '{color_name}'")
        
        try:
            hex_color = get_hex_color(color_name)
            
            if hex_color:
                logger.info(f"Found hex code for '{color_name}': {hex_color.hex_code}")
            else:
                logger.warning(f"No hex code found for color '{color_name}'")
            
            return hex_color
            
        except Exception as e:
            logger.error(f"Error getting hex color: {e}")
            raise
    
    # Register resources
    @mcp.resource("cheerlights://current")
    async def current_color_resource() -> str:
        """Current CheerLights color as a resource."""
        try:
            async with ThingSpeakClient() as client:
                current = await client.get_current_color()
                if current:
                    return f"Current CheerLights color: {current.color} (updated: {current.timestamp})"
                return "Current CheerLights color: unknown"
        except Exception as e:
            return f"Error fetching current color: {e}"
    
    @mcp.resource("cheerlights://history/{count}")
    async def history_resource(count: str) -> str:
        """CheerLights color history as a resource."""
        try:
            count_int = min(max(int(count), 1), 50)  # Limit for resource
            async with ThingSpeakClient() as client:
                colors = await client.get_color_history(count=count_int)
                
                if not colors:
                    return "No color history available"
                
                lines = [f"CheerLights Color History (last {len(colors)} changes):"]
                for i, color_data in enumerate(colors, 1):
                    lines.append(f"{i}. {color_data.color} at {color_data.timestamp}")
                
                return "\n".join(lines)
        except Exception as e:
            return f"Error fetching color history: {e}"
    
    @mcp.resource("cheerlights://colors/supported")
    async def supported_colors_resource() -> str:
        """List of supported CheerLights colors."""
        from .utils.color_mapping import COLOR_HEX_MAP
        
        lines = ["Supported CheerLights Colors:"]
        for color_name, hex_code in sorted(COLOR_HEX_MAP.items()):
            lines.append(f"- {color_name}: {hex_code}")
        
        return "\n".join(lines)
    
    # Register prompts
    @mcp.prompt()
    async def analyze_cheerlights_trends(period: str = "recent", focus: str = "general") -> str:
        """Generate a prompt for analyzing CheerLights color trends.
        
        Args:
            period: Time period to analyze (recent, daily, weekly)
            focus: Analysis focus (general, popularity, transitions, patterns)
        """
        base_prompt = "Analyze the CheerLights color data and provide insights about "
        
        if focus == "popularity":
            analysis_focus = "which colors are most and least popular, including usage statistics"
        elif focus == "transitions":
            analysis_focus = "color transition patterns and frequency of changes"
        elif focus == "patterns":
            analysis_focus = "temporal patterns, such as time-of-day or seasonal trends"
        else:
            analysis_focus = "overall trends, popular colors, and interesting patterns"
        
        period_context = ""
        if period == "daily":
            period_context = " Focus on the last 24 hours of data."
        elif period == "weekly":
            period_context = " Focus on the last week of data."
        else:
            period_context = " Focus on recent data."
        
        return f"{base_prompt}{analysis_focus}.{period_context} Use the CheerLights tools to gather current data and provide a comprehensive analysis."
    
    @mcp.prompt()
    async def cheerlights_color_report(color: str = "red") -> str:
        """Generate a prompt for creating a detailed report about a specific color.
        
        Args:
            color: The color to analyze
        """
        return f"""Create a detailed report about the color '{color}' in the CheerLights network. Include:

1. Current status: Is {color} the current color?
2. Historical usage: How often has {color} been used recently?
3. Technical details: Hex code and RGB values for {color}
4. Context: When was {color} last used and for how long?
5. Comparison: How does {color}'s usage compare to other colors?

Use the CheerLights tools to gather this data and provide accurate, up-to-date information."""
    
    logger.info(f"CheerLights MCP server '{name}' created and configured")
    return mcp


def main() -> None:
    """Main entry point for the CheerLights MCP server."""
    import sys
    
    # Create server
    server = create_server()
    
    # Handle command line arguments
    transport = "stdio"
    if len(sys.argv) > 1:
        transport = sys.argv[1]
    
    logger.info(f"Starting CheerLights MCP server with {transport} transport")
    
    try:
        server.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
