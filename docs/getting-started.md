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
