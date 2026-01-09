# Contributing

## Development Setup

### Clone and install

```bash
gh repo clone matin/garth
cd garth
make install
```

This installs the package, dependencies, and pre-commit hooks.

### Sync dependencies

```bash
make sync
```

Force reinstall and sync lockfiles.

## Development Commands

### Code Quality

| Command | Description |
|---------|-------------|
| `make format` | Auto-format Python source files using ruff |
| `make lint` | Lint Python source files (ruff format check, ruff check, mypy) |
| `make codespell` | Run spellchecking |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests with coverage |
| `make testcov` | Run tests and generate coverage reports (HTML and XML) |
| `make all` | Run the complete CI pipeline (lint, codespell, testcov) |

### Testing Specific Components

```bash
# Run only stats module tests
uv run pytest tests/stats/ -v

# Run only data module tests
uv run pytest tests/data/ -v

# Run specific test file
uv run pytest tests/stats/test_training_status.py -v
```

### Utilities

| Command | Description |
|---------|-------------|
| `make clean` | Clear local caches and build artifacts |
| `make help` | Display all available commands |

## Project Architecture

Garth is organized into several key modules:

### Core Modules

- **`http.py`** - Central HTTP client (`Client` class) handling OAuth1/OAuth2
  authentication, session management, and API requests
- **`sso.py`** - Single Sign-On authentication logic for Garmin services
- **`auth_tokens.py`** - OAuth1Token and OAuth2Token classes for token management

### Data Access Layer

- **`data/`** - Raw data retrieval from Garmin Connect API
  - `body_battery/` - Body battery stress and readings data
  - `hrv.py` - Heart rate variability detailed data
  - `sleep.py` - Detailed sleep data with stages and movements
  - `weight.py` - Weight and body composition data

### Statistics Layer

- **`stats/`** - Processed statistics and aggregated data
  - Various daily/weekly stats classes (steps, stress, hydration, etc.)
  - Built on top of the data layer but provides summarized metrics

### User Management

- **`users/`** - User profile and settings management
  - `profile.py` - User profile information
  - `settings.py` - User preferences and configuration

### CLI Interface

- **`cli.py`** - Command-line interface for authentication and basic operations

## Testing Infrastructure

- Uses pytest with VCR cassettes for HTTP recording/playback
- Comprehensive test coverage across all modules
- Separate test directories mirroring source structure
- Coverage reporting with HTML and XML output
