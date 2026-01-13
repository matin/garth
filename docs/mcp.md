# MCP Server

[garth-mcp-server](https://github.com/matin/garth-mcp-server/) is a
Model Context Protocol (MCP) server that exposes Garmin Connect data to
AI assistants like Claude. It uses Garth as the underlying library for
authentication and API access.

## Installation

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "Garth - Garmin Connect": {
      "command": "uvx",
      "args": [
        "garth-mcp-server"
      ],
      "env": {
        "GARTH_TOKEN": "<output of `uvx garth login`>"
      }
    }
  }
}
```

!!! note
    Make sure the path for the `uvx` command is fully scoped as MCP doesn't
    use the same PATH your shell does. On macOS, it's typically
    `/Users/{user}/.local/bin/uvx`.

## Available Tools

### Health & Wellness

Uses garth's data classes for structured, validated responses:

| Tool | Description |
|------|-------------|
| `user_profile` | Get user profile information |
| `user_settings` | Get user settings and preferences |
| `nightly_sleep` | Get detailed sleep data with optional movement data |
| `daily_sleep` | Get daily sleep summary data |
| `daily_stress` / `weekly_stress` | Get stress data |
| `daily_intensity_minutes` | Get daily intensity minutes |
| `weekly_intensity_minutes` | Get weekly intensity minutes |
| `daily_body_battery` | Get body battery data |
| `daily_hydration` | Get hydration data |
| `daily_steps` / `weekly_steps` | Get steps data |
| `daily_hrv` / `hrv_data` | Get heart rate variability data |

### Activities

Access activity data from Garmin Connect:

| Tool | Description |
|------|-------------|
| `get_activities` | Get list of activities with optional filters |
| `get_activities_by_date` | Get activities for a specific date |
| `get_activity_details` | Get detailed activity information |
| `get_activity_splits` | Get activity lap/split data |
| `get_activity_weather` | Get weather data for activities |

### Additional Health Data

| Tool | Description |
|------|-------------|
| `get_body_composition` | Get body composition data |
| `get_respiration_data` | Get respiration data |
| `get_spo2_data` | Get SpO2 (blood oxygen) data |
| `get_blood_pressure` | Get blood pressure readings |

### Device & Gear

| Tool | Description |
|------|-------------|
| `get_devices` | Get connected devices |
| `get_device_settings` | Get device settings |
| `get_gear` | Get gear information |
| `get_gear_stats` | Get gear usage statistics |

### Utility Tools

| Tool | Description |
|------|-------------|
| `monthly_activity_summary` | Get monthly activity overview |
| `snapshot` | Get snapshot data for date ranges |
| `get_connectapi_endpoint` | Direct access to any Garmin Connect API endpoint |

## How It Works

The MCP server authenticates using a `GARTH_TOKEN` environment variable,
which contains the serialized OAuth tokens from garth. When you run
`garth login`, it outputs a base64-encoded token string that can be used
for headless authentication.

Each tool maps to either:

1. **Garth data classes** - Structured, validated responses using Garth's
   stats and data modules (e.g., `DailySleep`, `DailyStress`)
2. **Direct API calls** - Raw Garmin Connect API access via `connectapi()`
   for endpoints not yet wrapped by garth

## Example Usage

Once configured, you can ask your AI assistant questions like:

- "How did I sleep last night?"
- "Show me my stress levels for the past week"
- "What activities did I do this month?"
- "What's my current body battery?"
