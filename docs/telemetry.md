# Telemetry

Garth supports optional telemetry using [Pydantic Logfire](https://pydantic.dev/logfire)
for logging and observability. Telemetry is **disabled by default** and is
**isolated to garth's requests only** - it won't affect other HTTP clients in
your application.

## Enable telemetry

Via environment variables:

```bash
export GARTH_TELEMETRY=true
export LOGFIRE_TOKEN=your_write_token
```

Via code:

```python
garth.configure(
    telemetry_enabled=True,
    telemetry_token="your_write_token",
)
```

## Custom service name

```bash
export GARTH_TELEMETRY_SERVICE_NAME=my-fitness-app
```

```python
garth.configure(telemetry_service_name="my-fitness-app")
```

## Custom callback

To send telemetry data to a custom destination instead of Logfire:

```python
def my_telemetry_handler(data: dict):
    # data contains: method, url, status_code, request_headers,
    # request_body, response_headers, response_body
    print(f"{data['method']} {data['url']} -> {data['status_code']}")

garth.configure(
    telemetry_enabled=True,
    telemetry_callback=my_telemetry_handler,
)
```

When a custom callback is provided, logfire is not configured and all telemetry
data is passed to your callback instead.

## Use with existing logfire setup

If your application already configures logfire, garth will use your existing
configuration. Just enable telemetry without providing a token:

```python
import logfire
logfire.configure(token="your-app-token", service_name="your-app")

import garth
garth.configure(telemetry_enabled=True)  # Uses your existing logfire config
```

## Use alternative OTLP backend

To send traces to your own OpenTelemetry collector instead of Logfire Cloud:

```bash
export GARTH_TELEMETRY=true
export LOGFIRE_SEND_TO_LOGFIRE=false
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

```python
garth.configure(
    telemetry_enabled=True,
    telemetry_send_to_logfire=False,
)
```

## What gets logged

All garth requests log:

- Method, URL, status code
- Request headers (sanitized)
- Request body (sanitized)
- Response headers (sanitized)
- Response body (sanitized)

**Always redacted:** Authorization headers, cookies, passwords, tokens, and other
sensitive fields in request/response bodies.
