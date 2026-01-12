# Garth

Garmin SSO auth + Connect Python client

[![CI](https://github.com/matin/garth/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/matin/garth/actions/workflows/ci.yml?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](https://codecov.io/gh/matin/garth)
[![PyPI version](https://img.shields.io/pypi/v/garth.svg?logo=python&logoColor=brightgreen&color=brightgreen)](https://pypi.org/project/garth/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/garth)](https://pypistats.org/packages/garth)

## Why Garth?

Garth is meant for personal use and follows the philosophy that your data is
your data. You should be able to download it and analyze it in the way that
you'd like. In my case, that means processing with Google Colab, Pandas,
Matplotlib, etc.

There are already a few Garmin Connect libraries. Why write another?

### Authentication and stability

The most important reasoning is to build a library with authentication that
works on [Google Colab](https://colab.research.google.com/) and doesn't require
tools like Cloudscraper. Garth, in comparison:

1. Uses OAuth1 and OAuth2 token authentication after initial login
1. OAuth1 token survives for a year
1. Supports MFA
1. Auto-refresh of OAuth2 token when expired
1. Works on Google Colab
1. Uses Pydantic dataclasses to validate and simplify use of data
1. Full test coverage

### JSON vs HTML

Using `garth.connectapi()` allows you to make requests to the Connect API
and receive JSON vs needing to parse HTML. You can use the same endpoints the
mobile app uses.

This also goes back to authentication. Garth manages the necessary Bearer
Authentication (along with auto-refresh) necessary to make requests routed to
the Connect API.

## Quick Start

```bash
pip install garth
```

```python
import garth
from getpass import getpass

# Login and save session
garth.login(input("Email: "), getpass("Password: "))
garth.save("~/.garth")

# Later, resume the session
garth.resume("~/.garth")
```

## Next Steps

- [Getting Started](getting-started.md) - Detailed authentication and session management
- [Configuration](configuration.md) - Domain and proxy settings
- [API Reference](api/stats.md) - Explore available data types
- [Examples](examples.md) - Google Colab notebooks
