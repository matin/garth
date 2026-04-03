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
if result1 == "needs_mfa":
    # MFA is required - get code from your custom flow
    mfa_code = "123456"
    garth.resume_login(result2, mfa_code)
else:
    # No MFA required - result1 and result2 are the tokens
    oauth1, oauth2 = result1, result2
```

## Session Management

### Resume session

```python
import garth

garth.resume("~/.garth")
# Make an API call to verify the session works
garth.client.username
```

If the session file doesn't exist or the token has expired (~1 year lifetime),
you'll need to log in again.

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

Generate a `GARTH_TOKEN` using the CLI:

```bash
uvx garth login
```

For China region, use `--domain garmin.cn`:

```bash
uvx garth --domain garmin.cn login
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
