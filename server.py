#!/usr/bin/env python3

import httpx
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("cheerlights")

# Constants
THINGSPEAK_API_BASE = "https://api.thingspeak.com"
CHEERLIGHTS_CHANNEL = "1417"

async def fetch_cheerlights_data(results=1):
    """Fetch CheerLights data from ThingSpeak API.
    
    Args:
        results: Number of results to fetch (default: 1)
    
    Returns:
        Dictionary containing the API response or None if failed
    """
    url = f"{THINGSPEAK_API_BASE}/channels/{CHEERLIGHTS_CHANNEL}/feeds.json"
    params = {"results": results}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching CheerLights data: {e}")
            return None

def parse_color_data(data, count=1):
    """Parse color data from ThingSpeak response.
    
    Args:
        data: ThingSpeak API response
        count: Number of colors to return
        
    Returns:
        List of color data dictionaries
    """
    if not data or "feeds" not in data or not data["feeds"]:
        return []
    
    results = []
    for feed in data["feeds"][:count]:
        # Field 1 contains the color name in the ThingSpeak channel
        color = feed.get("field1", "unknown")
        
        # Convert created_at string to a more readable format
        created_at = feed.get("created_at", "")
        try:
            if created_at:
                dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                timestamp = "unknown"
        except Exception:
            timestamp = created_at  # Use original if parsing fails
        
        results.append({
            "color": color,
            "timestamp": timestamp,
            "entry_id": feed.get("entry_id", "unknown")
        })
    
    return results

@mcp.tool()
async def get_current_color() -> str:
    """Get the most recent CheerLights color.
    
    Returns:
        A string with the current color and timestamp.
    """
    data = await fetch_cheerlights_data(results=1)
    
    if not data or "feeds" not in data or not data["feeds"]:
        return "Unable to fetch the current CheerLights color."
    
    color_data = parse_color_data(data, count=1)
    
    if not color_data:
        return "Unable to parse the current CheerLights color."
    
    color_info = color_data[0]
    return f"The current CheerLights color is {color_info['color']} (as of {color_info['timestamp']})."

@mcp.tool()
async def get_color_history(count: int = 5) -> str:
    """Get a history of recent CheerLights colors.
    
    Args:
        count: Number of colors to return (default: 5, max: 100)
    
    Returns:
        A formatted string with recent color changes.
    """
    # Enforce reasonable limits
    if count < 1:
        count = 1
    if count > 100:
        count = 100
        
    data = await fetch_cheerlights_data(results=count)
    
    if not data or "feeds" not in data or not data["feeds"]:
        return "Unable to fetch CheerLights color history."
    
    color_data = parse_color_data(data, count=count)
    
    if not color_data:
        return "Unable to parse CheerLights color history."
    
    result = f"Recent CheerLights color history (last {len(color_data)} changes):\n\n"
    
    for idx, color_info in enumerate(color_data, 1):
        result += f"{idx}. {color_info['color']} (at {color_info['timestamp']})\n"
    
    return result

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')