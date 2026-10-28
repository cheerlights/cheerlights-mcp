# Tools, resources, and prompts

Reference for the CheerLights MCP server, version 3.0.0.
All data comes from the public CheerLights feed on ThingSpeak, channel 1417.
Times are UTC in ISO 8601.
Lists of changes are newest first.

## Tools

Every tool is read-only (`readOnlyHint`) and returns structured output with a JSON schema.
A tool that fails returns an error result (`isError`) with a message an assistant can act on.

### `get_current_cheerlights_color`

The color every CheerLights light shows right now.

No parameters.

Returns a color change:

| Field | Type | Meaning |
|---|---|---|
| `color` | string | Color name, for example `purple` |
| `hex` | string | HEX value as published by CheerLights, for example `#800080` |
| `set_at` | datetime | When the color was set |
| `entry_id` | integer | ThingSpeak entry number of the change |

### `get_cheerlights_history`

Recent color changes, newest first.

| Parameter | Type | Range | Default |
|---|---|---|---|
| `count` | integer | 1 to 100 | 10 |

Returns `changes` (a list of color changes, as above) and `count`.

### `analyze_color_statistics`

How often each color was picked across recent changes.

| Parameter | Type | Range | Default |
|---|---|---|---|
| `sample_size` | integer | 10 to 8000 | 500 |

Returns `sample_size`, `period_start` and `period_end` (the oldest and newest change analyzed), `counts` (picks per color, most picked first), `most_popular`, `least_popular`, and `unique_colors`.

### `search_colors`

When a color was picked recently, newest first.

| Parameter | Type | Range | Default |
|---|---|---|---|
| `color` | string | one of the eleven CheerLights colors | required |
| `limit` | integer | 1 to 100 | 20 |
| `within` | integer | 1 to 8000 | 1000 |

`within` is how many recent changes to search.
Color names ignore case and spaces, so `Old Lace` matches `oldlace`.
Returns `color`, `searched`, `matches` (color changes), and `match_count`.

### `get_hex_color_code`

The HEX and RGB values of a CheerLights color.

| Parameter | Type | Range | Default |
|---|---|---|---|
| `color_name` | string | one of the eleven CheerLights colors | required |

Returns `name`, `hex`, and `rgb` (`red`, `green`, `blue`, each 0 to 255).
This tool does not call ThingSpeak.

## The eleven CheerLights colors

| Name | HEX |
|---|---|
| red | `#ff0000` |
| green | `#008000` |
| blue | `#0000ff` |
| cyan | `#00ffff` |
| white | `#ffffff` |
| oldlace | `#fdf5e6` |
| purple | `#800080` |
| magenta | `#ff00ff` |
| yellow | `#ffff00` |
| orange | `#ffa500` |
| pink | `#ffc0cb` |

Any other name, for example `lime`, returns an error that lists these.

## Resources

All resources are `application/json`.

| URI | Content |
|---|---|
| `cheerlights://current` | The current color change |
| `cheerlights://history/{count}` | The last `count` changes (1 to 100), newest first |
| `cheerlights://colors` | The eleven colors with HEX and RGB values |

## Prompts

| Prompt | Arguments | What it asks for |
|---|---|---|
| `analyze_cheerlights_trends` | `focus`: `popularity`, `streaks`, or `time of day` | An analysis of recent picks, with the numbers and the period they cover |
| `cheerlights_color_report` | `color` | A short report on one color: current or not, HEX and RGB, how often it was picked, when it was last picked |

## Transports

`cheerlights-mcp` serves over stdio by default, which desktop AI apps use.
`cheerlights-mcp streamable-http --host 127.0.0.1 --port 8000` serves over HTTP at `/mcp`; `sse` is also available for older clients.
