# Getting Started

## Installation

### From PyPI

```bash
python -m pip install garth
```

### From source

```bash
gh repo clone matin/garth
cd garth
make install
```

Use `make help` to see all available development commands.

## Authentication

### Basic login

```python
import garth
from getpass import getpass

email = input("Enter email address: ")
password = getpass("Enter password: ")
# If there's MFA, you'll be prompted during the login
garth.login(email, password)

garth.save("~/.garth")
```

### Custom MFA handler

By default, MFA will prompt for the code in the terminal. You can provide your
own handler:

```python
garth.login(email, password, prompt_mfa=lambda: input("Enter MFA code: "))
```

### Advanced MFA handling

For advanced use cases (like async handling), MFA can be handled separately:

```python
result1, result2 = garth.login(email, password, return_on_mfa=True)
if result1 == "needs_mfa":  # MFA is required
    mfa_code = "123456"  # Get this from your custom MFA flow
    oauth1, oauth2 = garth.resume_login(result2, mfa_code)
```

## Session Management

### Save session

After logging in, save the session to avoid logging in again:

```python
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
```

### Auto-resume from environment variables

Garth can automatically restore your session from environment variables when
the client is initialized. This is useful for scripts, containers, and CI/CD
pipelines.

**Using `GARTH_HOME`** (directory path):

```bash
export GARTH_HOME=~/.garth
```

```python
import garth
# Session is automatically loaded from ~/.garth
garth.client.username
```

**Using `GARTH_TOKEN`** (base64-encoded token):

```bash
export GARTH_TOKEN="eyJvYXV0aF90b2tlbi..."
```

```python
import garth
# Session is automatically loaded from the token
garth.client.username
```

Generate a `GARTH_TOKEN` using:

```bash
uvx garth login
```

!!! warning "Mutual exclusivity"
    `GARTH_HOME` and `GARTH_TOKEN` cannot both be set. Garth will raise a
    `GarthException` if both environment variables are present.

!!! tip "Auto-persist on token refresh"
    When using `GARTH_HOME`, refreshed OAuth2 tokens are automatically
    persisted back to the directory, keeping your session current.

!!! note "Token lifetime"
    The OAuth1 token survives for approximately one year. The OAuth2 token
    auto-refreshes as needed when making API calls.

## CLI Authentication

You can also authenticate using the command line:

```bash
uvx garth login
```

For China region:

```bash
uvx garth --domain garmin.cn login
```

This generates a `GARTH_TOKEN` that can be used with tools like
[garth-mcp-server](https://github.com/matin/garth-mcp-server).
