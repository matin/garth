# Garth

[![CI](https://github.com/matin/garth/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/matin/garth/actions/workflows/ci.yml?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](https://codecov.io/gh/matin/garth)
[![PyPI version](https://img.shields.io/pypi/v/garth.svg?logo=python&logoColor=brightgreen&color=brightgreen)](https://pypi.org/project/garth/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/garth)](https://pypistats.org/packages/garth)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue)](https://garth.readthedocs.io)

Garmin SSO auth + Connect Python client

## Features

- OAuth1/OAuth2 authentication (OAuth1 token lasts ~1 year)
- MFA support with custom handlers
- Auto-refresh of OAuth2 token
- Auto-resume from `GARTH_HOME` or `GARTH_TOKEN` environment variables
- Works on Google Colab
- Pydantic dataclasses for validated data
- Full test coverage

## Installation

```bash
pip install garth
```

## Quick Start

### Authenticate and save session

```python
import garth
from getpass import getpass

garth.login(input("Email: "), getpass("Password: "))
garth.save("~/.garth")
```

### Resume session

```python
import garth
from garth.exc import GarthException

garth.resume("~/.garth")
try:
    garth.client.username
except GarthException:
    # Session is expired. You'll need to log in again
    pass
```

Or use environment variables for automatic session restoration:

```bash
export GARTH_HOME=~/.garth
# or
export GARTH_TOKEN="eyJvYXV0aF90b2tlbi..."  # from `uvx garth login`
```

```python
import garth
# Session is automatically loaded
garth.client.username
```

### Fetch data

```python
# Get daily stress
garth.DailyStress.list("2023-07-23", 7)

# Get sleep data
garth.SleepData.get("2023-07-20")

# Get weight
garth.WeightData.list("2025-06-01", 30)

# Direct API calls
garth.connectapi("/usersummary-service/stats/stress/weekly/2023-07-05/52")
```

## Documentation

Full documentation at **[garth.readthedocs.io](https://garth.readthedocs.io)**

## MCP Server

[`garth-mcp-server`](https://github.com/matin/garth-mcp-server) is in early development.

To generate your `GARTH_TOKEN`, use `uvx garth login`.

## Star History

<!-- markdownlint-disable MD013 -->
<a href="https://www.star-history.com/#matin/garth&Date">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=matin/garth&type=Date&theme=dark" />
        <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=matin/garth&type=Date" />
        <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=matin/garth&type=Date" />
    </picture>
</a>
<!-- markdownlint-enable MD013 -->
