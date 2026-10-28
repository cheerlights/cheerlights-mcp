"""The CheerLights MCP server: tools, resources, and prompts over the live CheerLights color."""

import argparse
import json
import logging
from collections import Counter
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Literal

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ResourceError, ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from .colors import PALETTE, normalize, palette, palette_color
from .models import ColorChange, ColorHistory, ColorSearchResult, ColorStatistics, PaletteColor
from .thingspeak import MAX_RESULTS, ThingSpeakClient, ThingSpeakError

logger = logging.getLogger("cheerlights_mcp")

try:
    __version__ = version("cheerlights-mcp")
except PackageNotFoundError:  # running from a source checkout without installing
    __version__ = "0.0.0"

INSTRUCTIONS = """\
CheerLights is a global network of lights that all show the same color. Anyone sets the color \
on the CheerLights Discord with the /cheerlights command; these tools read it. They cannot set it.

The color is always one of eleven names: red, green, blue, cyan, white, oldlace, purple, magenta, \
yellow, orange, pink. History, statistics, and search cover the CheerLights ThingSpeak channel \
1417 and list changes newest first. Times are UTC."""

# Every tool only reads the public CheerLights feed on ThingSpeak.
READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=True)


def create_server(transport: httpx.AsyncBaseTransport | None = None) -> MCPServer:
    """Build the CheerLights MCP server.

    `transport` replaces the HTTP transport to ThingSpeak, for tests.
    """
    feed: dict[str, ThingSpeakClient] = {}

    @asynccontextmanager
    async def lifespan(_: MCPServer) -> AsyncIterator[None]:
        async with ThingSpeakClient(transport=transport) as client:
            feed["client"] = client
            yield
            feed.clear()

    mcp = MCPServer(
        name="cheerlights",
        title="CheerLights",
        version=__version__,
        website_url="https://cheerlights.com",
        instructions=INSTRUCTIONS,
        lifespan=lifespan,
    )

    async def recent(count: int) -> list[ColorChange]:
        try:
            return await feed["client"].recent_changes(count)
        except ThingSpeakError as e:
            raise ToolError(f"Could not read the CheerLights feed: {e}") from e

    def known_color(name: str) -> str:
        key = normalize(name)
        if key not in PALETTE:
            raise ToolError(f"'{name}' is not a CheerLights color. The colors are: {', '.join(PALETTE)}.")
        return key

    @mcp.tool(title="Current CheerLights color", annotations=READ_ONLY)
    async def get_current_cheerlights_color() -> ColorChange:
        """The color every CheerLights light shows right now: its name, HEX value, and when it was set."""
        changes = await recent(1)
        if not changes:
            raise ToolError("The CheerLights feed returned no color.")
        return changes[0]

    @mcp.tool(title="CheerLights color history", annotations=READ_ONLY)
    async def get_cheerlights_history(
        count: Annotated[int, Field(ge=1, le=100, description="How many recent changes to return")] = 10,
    ) -> ColorHistory:
        """Recent CheerLights color changes, newest first."""
        changes = await recent(count)
        return ColorHistory(changes=changes, count=len(changes))

    @mcp.tool(title="CheerLights color statistics", annotations=READ_ONLY)
    async def analyze_color_statistics(
        sample_size: Annotated[
            int, Field(ge=10, le=MAX_RESULTS, description="How many recent changes to analyze")
        ] = 500,
    ) -> ColorStatistics:
        """How often each color was picked across recent changes, with the most and least popular."""
        changes = await recent(sample_size)
        counts = Counter(change.color for change in changes).most_common()
        return ColorStatistics(
            sample_size=len(changes),
            period_start=changes[-1].set_at if changes else None,
            period_end=changes[0].set_at if changes else None,
            counts=dict(counts),
            most_popular=counts[0][0] if counts else None,
            least_popular=counts[-1][0] if counts else None,
            unique_colors=len(counts),
        )

    @mcp.tool(title="Search CheerLights history", annotations=READ_ONLY)
    async def search_colors(
        color: Annotated[str, Field(description="A CheerLights color name, for example purple")],
        limit: Annotated[int, Field(ge=1, le=100, description="Most matches to return")] = 20,
        within: Annotated[
            int, Field(ge=1, le=MAX_RESULTS, description="How many recent changes to search")
        ] = 1000,
    ) -> ColorSearchResult:
        """When a color was picked recently, newest first."""
        key = known_color(color)
        changes = await recent(within)
        matches = [change for change in changes if change.color == key][:limit]
        return ColorSearchResult(color=key, searched=len(changes), matches=matches, match_count=len(matches))

    @mcp.tool(title="CheerLights color HEX and RGB", annotations=ToolAnnotations(read_only_hint=True))
    async def get_hex_color_code(
        color_name: Annotated[str, Field(description="A CheerLights color name, for example oldlace")],
    ) -> PaletteColor:
        """The HEX and RGB values of a CheerLights color."""
        entry = palette_color(known_color(color_name))
        assert entry is not None
        return entry

    @mcp.resource(
        "cheerlights://current",
        title="Current CheerLights color",
        description="The current color as JSON",
        mime_type="application/json",
    )
    async def current_resource() -> str:
        try:
            change = await feed["client"].current()
        except ThingSpeakError as e:
            raise ResourceError(f"Could not read the CheerLights feed: {e}") from e
        return change.model_dump_json()

    @mcp.resource(
        "cheerlights://history/{count}",
        title="CheerLights color history",
        description="The last 1 to 100 color changes as JSON, newest first",
        mime_type="application/json",
    )
    async def history_resource(count: str) -> str:
        if not count.isdigit() or not 1 <= int(count) <= 100:
            raise ResourceError("count must be a number from 1 to 100")
        try:
            changes = await feed["client"].recent_changes(int(count))
        except ThingSpeakError as e:
            raise ResourceError(f"Could not read the CheerLights feed: {e}") from e
        return ColorHistory(changes=changes, count=len(changes)).model_dump_json()

    @mcp.resource(
        "cheerlights://colors",
        title="CheerLights colors",
        description="The eleven CheerLights colors with HEX and RGB values, as JSON",
        mime_type="application/json",
    )
    def colors_resource() -> str:
        return json.dumps([entry.model_dump() for entry in palette()])

    @mcp.prompt(title="Analyze CheerLights trends")
    def analyze_cheerlights_trends(
        focus: Literal["popularity", "streaks", "time of day"] = "popularity",
    ) -> str:
        """Ask for an analysis of recent CheerLights color picks."""
        return (
            f"Analyze recent CheerLights color picks, focusing on {focus}. Use the CheerLights tools "
            "to get the data (statistics over the last 1000 changes is a good start), cite the numbers "
            "you use, and say which period they cover."
        )

    @mcp.prompt(title="CheerLights color report")
    def cheerlights_color_report(color: str = "red") -> str:
        """Ask for a report on one CheerLights color."""
        return (
            f"Write a short report on the CheerLights color '{color}': whether it is the current color, "
            "its HEX and RGB values, how often it was picked in the last 1000 changes compared with the "
            "other colors, and when it was last picked. Use the CheerLights tools for every fact."
        )

    return mcp


def main() -> None:
    """Run the server. Defaults to stdio, the transport desktop AI apps use."""
    parser = argparse.ArgumentParser(prog="cheerlights-mcp", description="CheerLights MCP server")
    parser.add_argument("transport", nargs="?", default="stdio", choices=["stdio", "streamable-http", "sse"])
    parser.add_argument("--host", default="127.0.0.1", help="host for streamable-http or sse")
    parser.add_argument("--port", type=int, default=8000, help="port for streamable-http or sse")
    args = parser.parse_args()

    # stdout carries the MCP protocol over stdio, so logs go to stderr.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    server = create_server()
    if args.transport == "stdio":
        server.run()
    else:
        server.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
