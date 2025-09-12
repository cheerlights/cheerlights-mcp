# CheerLights MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-2.0-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Model Context Protocol (MCP) server that provides comprehensive access to the CheerLights API. CheerLights is a global IoT project that synchronizes colors across thousands of connected lights worldwide, creating a real-time shared experience.

## 🌈 Features

### Tools (Actions)
- **Current Color**: Get the most recent CheerLights color from the global network
- **Color History**: Retrieve recent color changes with configurable count (1-100)
- **Color Statistics**: Analyze color usage patterns and popularity over time
- **Color Search**: Find specific colors in the historical data
- **Hex Color Codes**: Get hex codes and RGB values for CheerLights colors

### Resources (Context)
- **Current Color Resource**: Real-time current color as a readable resource
- **History Resource**: Formatted color history for context injection
- **Supported Colors**: Complete list of valid CheerLights colors with hex codes

### Prompts (Templates)
- **Trend Analysis**: Generate prompts for analyzing CheerLights color trends
- **Color Reports**: Create detailed reports about specific colors

## 🚀 Quick Start

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/cheerlights/cheerlights-mcp.git
cd cheerlights-mcp

# Install with uv
uv sync

# Run the server
uv run cheerlights-mcp
```

### Using pip

```bash
# Clone and install
git clone https://github.com/cheerlights/cheerlights-mcp.git
cd cheerlights-mcp
pip install -e .

# Run the server
python -m cheerlights_mcp.server
```

## 📦 Installation

### For Development

```bash
# Install with development dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### From PyPI (when published)

```bash
pip install cheerlights-mcp
```

## 🔧 Usage

### With Claude Desktop

Add to your Claude Desktop configuration:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
    "mcpServers": {
        "cheerlights": {
            "command": "uv",
            "args": ["run", "cheerlights-mcp"],
            "cwd": "/path/to/cheerlights-mcp"
        }
    }
}
```

### Direct Execution

```bash
# Standard I/O (default)
python -m cheerlights_mcp.server

# With specific transport
python -m cheerlights_mcp.server stdio
python -m cheerlights_mcp.server sse
python -m cheerlights_mcp.server streamable-http
```

### Programmatic Usage

```python
from cheerlights_mcp import create_server

# Create and run server
server = create_server("My CheerLights Server")
server.run()
```

## 🛠️ API Reference

### Tools

#### `get_current_cheerlights_color()`
Returns structured `ColorData` with:
- `color`: Current color name
- `timestamp`: When it was set
- `entry_id`: Unique identifier
- `created_at`: Parsed datetime (optional)

#### `get_cheerlights_history(count: int = 5)`
Returns `ColorHistory` with recent changes (1-100 entries).

#### `analyze_color_statistics(sample_size: int = 50)`
Returns `ColorStatistics` with:
- Color frequency counts
- Most/least popular colors
- Analysis period information
- Unique color count

#### `search_colors(color: str, limit: int = 20)`
Returns `ColorSearchResult` with matching entries.

#### `get_hex_color_code(color_name: str)`
Returns `HexColor` with hex code and RGB values.

### Resources

- `cheerlights://current` - Current color status
- `cheerlights://history/{count}` - Recent color history
- `cheerlights://colors/supported` - All supported colors

### Example Queries for Claude

- "What's the current CheerLights color and when was it last changed?"
- "Show me the last 20 CheerLights color changes"
- "Analyze the color usage statistics for the last 100 changes"
- "Search for all recent times the color was 'blue'"
- "What's the hex code for the CheerLights 'warmwhite' color?"
- "Create a report on CheerLights color trends"

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=cheerlights_mcp

# Run specific test files
uv run pytest tests/test_tools.py -v
```

## 🏗️ Architecture

```
cheerlights-mcp/
├── src/cheerlights_mcp/
│   ├── api/              # ThingSpeak API client
│   ├── models/           # Pydantic data models
│   ├── tools/            # MCP tool implementations
│   ├── utils/            # Utilities (color mapping, statistics)
│   └── server.py         # Main FastMCP server
├── tests/                # Comprehensive test suite
└── examples/             # Usage examples
```

### Key Components

- **ThingSpeakClient**: Async HTTP client for CheerLights API
- **Pydantic Models**: Type-safe data validation and serialization
- **Structured Output**: Full support for MCP structured responses
- **Comprehensive Error Handling**: Graceful degradation and logging
- **Statistics Engine**: Color usage analysis and trend calculation

## 🎨 Supported Colors

CheerLights supports these standard colors:

- **Primary**: red, green, blue
- **Secondary**: cyan, magenta, yellow
- **Extended**: orange, pink, purple, white, warmwhite, oldlace
- **Utility**: black

Each color includes hex codes and RGB values for precise representation.

## 📊 Example Data

### Current Color Response
```json
{
  "color": "red",
  "timestamp": "2024-01-15 14:30:22 UTC",
  "entry_id": "12345",
  "created_at": "2024-01-15T14:30:22Z"
}
```

### Statistics Response
```json
{
  "color_counts": {"red": 15, "blue": 12, "green": 8},
  "most_popular": "red",
  "least_popular": "green", 
  "total_changes": 35,
  "unique_colors": 3,
  "analysis_period": "2 hours"
}
```

### Development Setup

```bash
# Clone and setup
git clone https://github.com/cheerlights/cheerlights-mcp.git
cd cheerlights-mcp
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest -v
```

## 📝 Changelog

### Version 2.0.0

- **Complete rewrite** using modern MCP Python SDK
- **Structured Output** support for all tools
- **Enhanced API client** with proper error handling
- **Comprehensive test suite** with >90% coverage
- **Type safety** with Pydantic models throughout
- **New tools**: statistics, search, hex color codes
- **Resources and prompts** for richer integration
- **Modern packaging** with uv and pyproject.toml

### Version 1.0.0

- Initial FastMCP implementation
- Basic current color and history tools
- Simple ThingSpeak integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **CheerLights Project**: [cheerlights.com](https://cheerlights.com)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **ThingSpeak API**: [thingspeak.com](https://thingspeak.com)
- **Original Tutorial**: [Creating MCP Servers](https://nothans.com/learn-how-to-create-your-own-mcp-server-for-claude-desktop-and-windsurf)

## 🎄 About CheerLights

CheerLights is a global Internet of Things project that synchronizes colored lights all around the world to create a synchronized light display. The project was created by Hans Scharler and has connected thousands of lights across the globe since 2011. When someone changes the color on the [CheerLights Discord Server](https://cheerlights/discord), all participating lights change to that color in near real-time.

This MCP server provides AI assistants with rich access to CheerLights data, enabling analysis of global lighting trends, color popularity, and temporal patterns in this unique IoT dataset.
