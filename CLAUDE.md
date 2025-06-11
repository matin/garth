# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

## Development Commands

### Setup and Installation

- `make install` - Install package, dependencies, and pre-commit hooks for
  local development
- `make sync` - Sync dependencies and lockfiles (includes force reinstall)

### Code Quality

- `make lint` - Run full linting (ruff format check, ruff check, mypy)
- `make format` - Auto-format code with ruff
- `make codespell` - Run spellchecking

### Testing

- `make test` - Run all tests with coverage
- `make testcov` - Run tests and generate coverage reports (HTML + XML)
- `uv run pytest tests/path/to/test.py::test_name -v` - Run a single test
- `uv run pytest tests/stats/ -v` - Run tests for a specific module

### Complete Workflow

- `make all` - Run the full CI pipeline (lint + codespell + testcov)

## Architecture Overview

### Core Structure

Garth is a Garmin Connect API client that uses OAuth1/OAuth2 authentication.
The main components:

- **Authentication Layer**: `auth_tokens.py`, `sso.py` - Handles OAuth1/OAuth2
  tokens and Garmin SSO
- **HTTP Client**: `http.py` - Main client with automatic token refresh and
  request handling
- **Data Models**: `data/`, `stats/`, `users/` - Pydantic dataclasses for
  different API endpoints
- **CLI**: `cli.py` - Command-line interface for authentication

### Data Module Pattern

All data modules follow a consistent pattern:

- Extend base classes (`_base.py` in stats, similar patterns elsewhere)
- Use Pydantic dataclasses for validation
- Implement `.list()` class methods for fetching collections
- Implement `.get()` class methods for individual items
- Handle API pagination automatically

### Stats Module Architecture

The stats module (`src/garth/stats/`) follows a specific inheritance pattern:

- `_base.py` contains the `Stats` base class with common `.list()` implementation
- Individual stat types (stress, sleep, HRV, etc.) inherit from `Stats`
- Each class defines `_path` and `_page_size` class variables
- API responses are automatically converted from camelCase to snake_case

### Testing Strategy

- Uses pytest with VCR.py for HTTP request recording
- Cassettes stored in `tests/*/cassettes/` directories
- `authed_client` fixture provides authenticated client for tests
- Environment variable `GARTH_HOME` controls whether to record new cassettes
  or use existing ones
- Request/response sanitization removes sensitive data from cassettes

### Authentication Flow

1. Initial login with email/password (supports MFA)
2. Receives OAuth1 token (long-lived, ~1 year)
3. Exchanges for OAuth2 token (short-lived, auto-refreshed)
4. Tokens can be saved/loaded from files for persistence

### Adding New Stats Endpoints

When adding new stats endpoints (like training status):

1. Create new module in `src/garth/stats/`
2. Define dataclasses extending `Stats` base class
3. Add imports to `src/garth/stats/__init__.py`
4. Add exports to `src/garth/__init__.py`
5. Create comprehensive tests in `tests/stats/`
6. Run tests to generate VCR cassettes
7. Update README.md with usage examples

### Key Patterns

- Use `garth.connectapi()` for direct API access with automatic authentication
- API endpoints follow Garmin's internal mobile app structure
- Dates are handled as `datetime.date` objects
- All optional fields default to `None` in dataclasses
- Custom parsing logic in training status module shows how to handle complex
  nested API responses

### Code Quality Guidelines

- never use `# type: ignore`
