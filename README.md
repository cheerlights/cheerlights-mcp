# CheerLights MCP Server

A Model Context Protocol (MCP) server that allows Claude or other AI tools to interact with the CheerLights API. CheerLights is a global IoT project that synchronizes colors across connected lights worldwide.

## Features

- Get the current CheerLights color
- View recent color change history
- Real-time integration with the CheerLights API

## Installation

First, install the necessary dependencies:

```bash
pip install mcp httpx
```

## Running the Server

Save the code to a file (e.g., `server.py`) and run it:

```bash
python server.py
```

## Connecting to Claude for Desktop

Add this to your Claude for Desktop configuration:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
    "mcpServers": {
        "cheerlights": {
            "command": "python",
            "args": ["path/to/server.py"]
        }
    }
}
```

## Using with Claude

After restarting Claude for Desktop, you can ask questions like:

- "What's the current CheerLights color?"
- "Show me the last 10 CheerLights color changes"

## API Reference

The server uses the CheerLights API endpoint:
`http://api.thingspeak.com/channels/1417/field/1/last.json`

## Blog Tutorial

[Learn How to Create Your Own MCP Server for Claude Desktop and Windsurf](https://nothans.com/learn-how-to-create-your-own-mcp-server-for-claude-desktop-and-windsurf)
