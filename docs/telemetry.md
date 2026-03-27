# Telemetry

Garth includes built-in telemetry using
[Pydantic Logfire](https://pydantic.dev/logfire) for logging and observability.
Telemetry is **disabled by default** as of v0.8.0 since Garth is no longer
actively maintained.

## Disable telemetry

Via environment variable:

```bash
export GARTH_TELEMETRY_ENABLED=false
```

Via code:

```python
garth.configure(telemetry_enabled=False)
```

## Custom callback

To send telemetry data to a custom destination instead of Logfire:

```python
def my_telemetry_handler(data: dict):
    # data contains: session_id, method, url, status_code,
    # request_headers, request_body, response_headers, response_body
    print(f"{data['method']} {data['url']} -> {data['status_code']}")

garth.configure(
    telemetry_enabled=True,
    telemetry_callback=my_telemetry_handler,
)
```

When a custom callback is provided, logfire is not configured and all telemetry
data is passed to your callback instead.

## Configuration

Telemetry settings can be configured via environment variables with the
`GARTH_TELEMETRY_` prefix:

| Environment Variable | Default | Description |
|---|---|---|
| `GARTH_TELEMETRY_ENABLED` | `true` | Enable/disable telemetry |
| `GARTH_TELEMETRY_SEND_TO_LOGFIRE` | `true` | Send to Logfire Cloud |
| `GARTH_TELEMETRY_TOKEN` | *(built-in)* | Logfire write token |

## What gets logged

All garth HTTP requests log:

- Session ID (unique per garth session)
- Method, URL, status code
- Request headers (sanitized)
- Request body (sanitized)
- Response headers (sanitized)
- Response body (sanitized)

**Always redacted:** Authorization headers, cookies, passwords, tokens, and other
sensitive fields in request/response bodies.
