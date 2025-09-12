"""Example client for CheerLights MCP server.

This demonstrates how to connect to and interact with the CheerLights MCP server.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Run example client interactions with CheerLights MCP server."""
    # Set up server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "cheerlights_mcp.server"],
        env={}
    )
    
    print("🎄 CheerLights MCP Client Example")
    print("=" * 40)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("✅ Connected to CheerLights MCP server")
            
            # List available tools
            print("\n🔧 Available Tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # List available resources
            print("\n📊 Available Resources:")
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            
            # List available prompts
            print("\n💬 Available Prompts:")
            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            
            # Get current color
            print("\n🌈 Current CheerLights Color:")
            current_result = await session.call_tool("get_current_cheerlights_color", {})
            
            # Parse structured response
            if hasattr(current_result, 'structuredContent') and current_result.structuredContent:
                color_data = current_result.structuredContent
                print(f"  Color: {color_data.get('color')}")
                print(f"  Updated: {color_data.get('timestamp')}")
                print(f"  Entry ID: {color_data.get('entry_id')}")
            else:
                # Fallback to text content
                for content in current_result.content:
                    print(f"  {content.text}")
            
            # Get color history
            print("\n📈 Recent Color History (last 10):")
            history_result = await session.call_tool("get_cheerlights_history", {"count": 10})
            
            if hasattr(history_result, 'structuredContent') and history_result.structuredContent:
                history_data = history_result.structuredContent
                colors = history_data.get('colors', [])
                print(f"  Found {len(colors)} recent colors:")
                for i, color in enumerate(colors[:5], 1):  # Show first 5
                    print(f"    {i}. {color.get('color')} at {color.get('timestamp')}")
                if len(colors) > 5:
                    print(f"    ... and {len(colors) - 5} more")
            
            # Get hex color code
            print("\n🎨 Hex Color Code for 'red':")
            hex_result = await session.call_tool("get_hex_color_code", {"color_name": "red"})
            
            if hasattr(hex_result, 'structuredContent') and hex_result.structuredContent:
                hex_data = hex_result.structuredContent
                if hex_data:
                    print(f"  Hex Code: {hex_data.get('hex_code')}")
                    rgb = hex_data.get('rgb', {})
                    print(f"  RGB: R={rgb.get('red')}, G={rgb.get('green')}, B={rgb.get('blue')}")
                else:
                    print("  No hex code found for 'red'")
            
            # Get color statistics
            print("\n📊 Color Usage Statistics:")
            stats_result = await session.call_tool("analyze_color_statistics", {"sample_size": 50})
            
            if hasattr(stats_result, 'structuredContent') and stats_result.structuredContent:
                stats_data = stats_result.structuredContent
                print(f"  Analysis Period: {stats_data.get('analysis_period')}")
                print(f"  Total Changes: {stats_data.get('total_changes')}")
                print(f"  Unique Colors: {stats_data.get('unique_colors')}")
                print(f"  Most Popular: {stats_data.get('most_popular')}")
                print(f"  Least Popular: {stats_data.get('least_popular')}")
                
                # Show top color counts
                color_counts = stats_data.get('color_counts', {})
                if color_counts:
                    print("  Top Colors:")
                    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
                    for color, count in sorted_colors[:3]:
                        print(f"    - {color}: {count} times")
            
            # Search for specific color
            print("\n🔍 Search for 'blue' in history:")
            search_result = await session.call_tool("search_colors", {"color": "blue", "limit": 5})
            
            if hasattr(search_result, 'structuredContent') and search_result.structuredContent:
                search_data = search_result.structuredContent
                matches = search_data.get('matches', [])
                print(f"  Found {search_data.get('match_count', 0)} matches:")
                for match in matches:
                    print(f"    - {match.get('color')} at {match.get('timestamp')}")
            
            # Read a resource
            print("\n📄 Current Color Resource:")
            try:
                from pydantic import AnyUrl
                resource_content = await session.read_resource(AnyUrl("cheerlights://current"))
                if resource_content.contents:
                    print(f"  {resource_content.contents[0].text}")
            except Exception as e:
                print(f"  Error reading resource: {e}")
            
            # Get a prompt
            print("\n💭 Analysis Prompt Example:")
            try:
                prompt_result = await session.get_prompt("analyze_cheerlights_trends", {"period": "recent", "focus": "popularity"})
                if prompt_result.messages:
                    print(f"  {prompt_result.messages[0].content.text}")
            except Exception as e:
                print(f"  Error getting prompt: {e}")
            
            print("\n✨ Example completed!")
            print("The CheerLights MCP server provides rich structured data for")
            print("analyzing the global CheerLights network. Try integrating it")
            print("with Claude Desktop or your own MCP clients!")


if __name__ == "__main__":
    asyncio.run(main())
