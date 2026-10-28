"""Start the CheerLights MCP server over stdio, the way an AI app does, and call every tool.

uv run python examples/client_example.py
"""

import asyncio
import json
import sys

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


async def main() -> None:
    server = StdioServerParameters(command=sys.executable, args=["-m", "cheerlights_mcp.server"])
    async with Client(server) as client:
        print(f"Connected to {client.server_info.name} {client.server_info.version}")

        tools = (await client.list_tools()).tools
        print("Tools:", ", ".join(tool.name for tool in tools))

        calls = [
            ("get_current_cheerlights_color", {}),
            ("get_cheerlights_history", {"count": 3}),
            ("analyze_color_statistics", {"sample_size": 1000}),
            ("search_colors", {"color": "purple", "limit": 2}),
            ("get_hex_color_code", {"color_name": "oldlace"}),
        ]
        for name, arguments in calls:
            result = await client.call_tool(name, arguments)
            status = "error" if result.is_error else "ok"
            print(f"\n{name} {arguments} -> {status}")
            print(json.dumps(result.structured_content, indent=2, default=str)[:600])

        colors = await client.read_resource("cheerlights://colors")
        print("\ncheerlights://colors ->", len(json.loads(colors.contents[0].text)), "colors")


if __name__ == "__main__":
    asyncio.run(main())
