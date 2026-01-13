# Configuration

All configuration is done through `garth.configure()`. Options can be combined
in a single call.

## Domain Settings

### China region

For users in China, configure the domain to use `garmin.cn`:

```python
garth.configure(domain="garmin.cn")
```

## Proxy Settings

### Proxy through Charles

For debugging or monitoring HTTP traffic:

```python
garth.configure(proxies={"https": "http://localhost:8888"}, ssl_verify=False)
```

!!! warning "SSL verification"
    Disabling SSL verification (`ssl_verify=False`) should only be used for
    debugging purposes. Do not use in production.

### Custom proxy

```python
garth.configure(proxies={
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
})
```

## Request Settings

### Timeout

Set the request timeout in seconds (default: 10):

```python
garth.configure(timeout=30)
```

### Retries

Configure automatic retry behavior for failed requests:

```python
garth.configure(
    retries=5,                            # Max retry attempts (default: 3)
    status_forcelist=(408, 500, 502, 503, 504),  # HTTP codes to retry
    backoff_factor=1.0,                   # Delay multiplier between retries
)
```

!!! note "429 not retried by default"
    HTTP 429 (Too Many Requests) is not in the default retry list because
    retrying can make rate limiting worse. Add it explicitly if needed:
    `status_forcelist=(408, 429, 500, 502, 503, 504)`

## Connection Pool Settings

For high-throughput applications:

```python
garth.configure(
    pool_connections=20,  # Number of connection pools (default: 10)
    pool_maxsize=20,      # Max connections per pool (default: 10)
)
```
