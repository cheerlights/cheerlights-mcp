# CheerLights MCP server

An MCP server that lets Claude and other AI assistants read the live CheerLights color, its history, and statistics.

[![PyPI](https://img.shields.io/pypi/v/cheerlights-mcp)](https://pypi.org/project/cheerlights-mcp/) [![Python](https://img.shields.io/pypi/pyversions/cheerlights-mcp)](https://pypi.org/project/cheerlights-mcp/) [![CI](https://github.com/cheerlights/cheerlights-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/cheerlights/cheerlights-mcp/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/cheerlights/cheerlights-mcp/blob/main/LICENSE)

[CheerLights](https://cheerlights.com) is a global network of lights that all show the same color, set by anyone on the [CheerLights Discord](https://cheerlights.com/discord).
This server reads the public CheerLights feed (ThingSpeak channel 1417) and gives an assistant five read-only tools: the current color, recent history, statistics, search, and HEX and RGB values.
It is built on the MCP Python SDK 2.x and needs no API key.

## Quick start

You need [uv](https://docs.astral.sh/uv/), which installs Python 3.10 or later for you.
`uvx` runs the server straight from [PyPI](https://pypi.org/project/cheerlights-mcp/), with nothing else to install.

Add the server to Claude Code:

```bash
claude mcp add cheerlights -- uvx cheerlights-mcp
```

Or add it to Claude Desktop's `claude_desktop_config.json` and restart the app:

```json
{
  "mcpServers": {
    "cheerlights": {
      "command": "uvx",
      "args": ["cheerlights-mcp"]
    }
  }
}
```

Then ask: "What's the current CheerLights color?"
The assistant calls `get_current_cheerlights_color` and answers with the live color.

## Example

These results come from a live run of version 3.0.0 over stdio on 2026-10-28 (`examples/client_example.py`).

`get_current_cheerlights_color` returns the color, its HEX value, and when it was set:

```json
{
  "color": "purple",
  "hex": "#800080",
  "set_at": "2026-10-28T15:46:23Z",
  "entry_id": 1067049
}
```

`analyze_color_statistics` with `sample_size` 1000 covered 2026-09-13 to 2026-10-28 (excerpt):

```json
{
  "sample_size": 1000,
  "counts": { "orange": 111, "blue": 109, "red": 105, "...": "...", "white": 15 },
  "most_popular": "orange",
  "least_popular": "white",
  "unique_colors": 11
}
```

## Tools

- `get_current_cheerlights_color`: the current color, its HEX value, and when it was set.
- `get_cheerlights_history`: the last 1 to 100 color changes, newest first.
- `analyze_color_statistics`: how often each color was picked across the last 10 to 8000 changes.
- `search_colors`: when a color was picked recently, newest first.
- `get_hex_color_code`: the HEX and RGB values of any of the eleven CheerLights colors.
- Resources `cheerlights://current`, `cheerlights://history/{count}`, and `cheerlights://colors`, as JSON.
- Prompts `analyze_cheerlights_trends` and `cheerlights_color_report`.

Every tool is marked read-only, returns structured output with a schema, and answers an unknown color with an error that lists the valid ones.

## Limits

- It reads the color; it cannot set it. People set the color on the CheerLights Discord with `/cheerlights`.
- History reaches back at most 8000 changes, the most ThingSpeak returns in one request.
- If ThingSpeak cannot be reached, the tools return an error saying so.

## Documentation

- [Tools, resources, and prompts](https://github.com/cheerlights/cheerlights-mcp/blob/main/docs/tools.md): every parameter, its range, and the fields each tool returns.
- [The CheerLights API](https://cheerlights.com/learn/): ThingSpeak, Adafruit IO, and MQTT feeds, for building without MCP.

## Development

```bash
git clone https://github.com/cheerlights/cheerlights-mcp
cd cheerlights-mcp
uv sync
uv run pytest
```

The 11 tests drive the server through an in-memory MCP client against a fake ThingSpeak.
`uv run python examples/client_example.py` starts the server over stdio and calls every tool against the live feed.
`uv run ruff check .` and `uv run mypy src` check style and types.
To serve over HTTP instead of stdio, run `uv run cheerlights-mcp streamable-http --port 8000`.

## License

MIT. See [LICENSE](https://github.com/cheerlights/cheerlights-mcp/blob/main/LICENSE).
