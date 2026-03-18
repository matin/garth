# Telemetry

Garth includes built-in telemetry using
[Pydantic Logfire](https://pydantic.dev/logfire) for logging and observability.
Telemetry is **enabled by default** to help diagnose authentication issues. It
is **isolated to Garth's requests only** — it won't affect other HTTP clients
in your application.

## Why telemetry is on by default

Garmin occasionally changes their authentication endpoints in ways that only
affect a subset of users — for example, the
[SSO migration](https://github.com/cyberjunky/python-garminconnect/issues/332)
that caused 403 errors for some users while others were unaffected. Without
telemetry, these issues are nearly impossible to reproduce or diagnose. With
default-on telemetry, maintainers can look up the exact request/response
sequence for a failing session using the session ID.

Each session generates a unique `session_id` that is printed to stdout when
garth is imported:

```text
Garth session: a01e3fc1d5ac4c9a
```

When reporting issues, include your session ID so maintainers can look up your
request logs.

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
