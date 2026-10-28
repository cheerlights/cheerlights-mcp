"""The server end to end: an MCP client calls the real tools, with ThingSpeak replaced by a fake."""

import json

import httpx
import pytest
from mcp.client import Client

from cheerlights_mcp import create_server

# Oldest first, the way ThingSpeak returns them.
FEEDS = [
    {"created_at": "2026-10-27T10:00:00Z", "entry_id": 1, "field1": "red", "field2": "#ff0000"},
    {"created_at": "2026-10-27T10:05:00Z", "entry_id": 2, "field1": "green", "field2": "#008000"},
    {"created_at": "2026-10-27T10:10:00Z", "entry_id": 3, "field1": "red", "field2": "#ff0000"},
    {"created_at": "2026-10-27T10:15:00Z", "entry_id": 4, "field1": "oldlace", "field2": "#fdf5e6"},
    {"created_at": "2026-10-27T10:20:00Z", "entry_id": 5, "field1": "purple", "field2": "#800080"},
]


def fake_thingspeak(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/channels/1417/feeds.json"
    results = int(request.url.params["results"])
    return httpx.Response(200, json={"channel": {"id": 1417}, "feeds": FEEDS[-results:]})


def broken_thingspeak(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503, text="unavailable")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def client(handler=fake_thingspeak) -> Client:
    return Client(create_server(transport=httpx.MockTransport(handler)))


@pytest.mark.anyio
async def test_tools_are_listed_read_only_with_titles() -> None:
    async with client() as c:
        tools = {tool.name: tool for tool in (await c.list_tools()).tools}
    assert set(tools) == {
        "get_current_cheerlights_color",
        "get_cheerlights_history",
        "analyze_color_statistics",
        "search_colors",
        "get_hex_color_code",
    }
    for tool in tools.values():
        assert tool.title
        assert tool.annotations is not None and tool.annotations.read_only_hint is True
        assert tool.output_schema is not None


@pytest.mark.anyio
async def test_current_color_has_name_hex_and_time() -> None:
    async with client() as c:
        result = await c.call_tool("get_current_cheerlights_color", {})
    assert not result.is_error
    assert result.structured_content == {
        "color": "purple",
        "hex": "#800080",
        "set_at": "2026-10-27T10:20:00Z",
        "entry_id": 5,
    }


@pytest.mark.anyio
async def test_history_is_newest_first() -> None:
    async with client() as c:
        result = await c.call_tool("get_cheerlights_history", {"count": 3})
    data = result.structured_content
    assert data["count"] == 3
    assert [change["color"] for change in data["changes"]] == ["purple", "oldlace", "red"]


@pytest.mark.anyio
async def test_history_count_is_validated_by_the_schema() -> None:
    async with client() as c:
        result = await c.call_tool("get_cheerlights_history", {"count": 500})
    assert result.is_error


@pytest.mark.anyio
async def test_statistics_count_picks_and_cover_the_period() -> None:
    async with client() as c:
        result = await c.call_tool("analyze_color_statistics", {"sample_size": 10})
    data = result.structured_content
    assert data["sample_size"] == 5
    assert data["counts"] == {"red": 2, "green": 1, "oldlace": 1, "purple": 1}
    assert data["most_popular"] == "red"
    assert data["unique_colors"] == 4
    assert data["period_start"] == "2026-10-27T10:00:00Z"
    assert data["period_end"] == "2026-10-27T10:20:00Z"


@pytest.mark.anyio
async def test_search_returns_newest_matches_first() -> None:
    async with client() as c:
        result = await c.call_tool("search_colors", {"color": "Red"})
    data = result.structured_content
    assert data["color"] == "red"
    assert [change["entry_id"] for change in data["matches"]] == [3, 1]


@pytest.mark.anyio
async def test_search_rejects_a_color_that_is_not_cheerlights() -> None:
    async with client() as c:
        result = await c.call_tool("search_colors", {"color": "lime"})
    assert result.is_error
    assert "not a CheerLights color" in result.content[0].text
    assert "oldlace" in result.content[0].text


@pytest.mark.anyio
async def test_hex_code_comes_from_the_palette() -> None:
    async with client() as c:
        result = await c.call_tool("get_hex_color_code", {"color_name": "Old Lace"})
    assert result.structured_content == {
        "name": "oldlace",
        "hex": "#fdf5e6",
        "rgb": {"red": 253, "green": 245, "blue": 230},
    }


@pytest.mark.anyio
async def test_feed_outage_is_a_clear_tool_error() -> None:
    async with client(broken_thingspeak) as c:
        result = await c.call_tool("get_current_cheerlights_color", {})
    assert result.is_error
    assert "Could not read the CheerLights feed" in result.content[0].text
    assert "503" in result.content[0].text


@pytest.mark.anyio
async def test_resources_return_json() -> None:
    async with client() as c:
        current = json.loads((await c.read_resource("cheerlights://current")).contents[0].text)
        history = json.loads((await c.read_resource("cheerlights://history/2")).contents[0].text)
        colors = json.loads((await c.read_resource("cheerlights://colors")).contents[0].text)
    assert current["color"] == "purple"
    assert [change["color"] for change in history["changes"]] == ["purple", "oldlace"]
    assert len(colors) == 11
    assert {"name": "green", "hex": "#008000", "rgb": {"red": 0, "green": 128, "blue": 0}} in colors


@pytest.mark.anyio
async def test_prompts_render() -> None:
    async with client() as c:
        prompts = {prompt.name for prompt in (await c.list_prompts()).prompts}
        report = await c.get_prompt("cheerlights_color_report", {"color": "cyan"})
    assert prompts == {"analyze_cheerlights_trends", "cheerlights_color_report"}
    assert "cyan" in report.messages[0].content.text
