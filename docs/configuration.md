# Configuration

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
