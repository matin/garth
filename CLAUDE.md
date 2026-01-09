# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Development Commands

### Setup and Installation

- `make install` - Install package, dependencies, and pre-commit hooks
- `make sync` - Sync dependencies and lockfiles (force reinstall)

### Code Quality and Testing

- `make format` - Auto-format Python source files using ruff
- `make lint` - Lint Python source files (ruff format check, ruff check, mypy)
- `make test` - Run all tests with coverage
- `make testcov` - Run tests and generate coverage reports (HTML and XML)
- `make all` - Run the complete CI pipeline (lint, codespell, testcov)

### Utilities

- `make clean` - Clear local caches and build artifacts
- `make codespell` - Run spellchecking
- `make help` - Display all available commands

### Testing Specific Components

- `uv run pytest tests/stats/ -v` - Run only stats module tests
- `uv run pytest tests/data/ -v` - Run only data module tests
- `uv run pytest tests/stats/test_training_status.py -v` - Run specific test

## Project Architecture

Garth is a Python library for Garmin Connect API access with OAuth
authentication. The codebase is organized into several key modules:

### Core Modules

- **`http.py`** - Central HTTP client (`Client` class) handling OAuth1/OAuth2
  authentication, session management, and API requests
- **`sso.py`** - Single Sign-On authentication logic for Garmin services
- **`auth_tokens.py`** - OAuth1Token and OAuth2Token classes for token
  management

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

## Key Design Patterns

### Authentication Flow

1. OAuth1 token obtained through SSO (lasts ~1 year)
2. OAuth2 token auto-refreshed as needed for API calls
3. MFA support with custom handlers
4. Session persistence via `save()` and `resume()` methods

### API Access

- Main client instance available as `garth.client`
- `connectapi()` method for direct API calls returning JSON
- Domain configuration support (garmin.com vs garmin.cn)

### Data Models

- Extensive use of Pydantic dataclasses for validation
- Consistent patterns across stats and data modules
- Date-based queries with period parameters

## Testing Infrastructure

- Uses pytest with VCR cassettes for HTTP recording/playback
- Comprehensive test coverage across all modules
- Separate test directories mirroring source structure
- Coverage reporting with HTML and XML output

## Git Workflow

- Always squash merge PRs and delete both remote and local branches
- Use `gh pr merge <number> --squash --delete-branch` followed by
  `git checkout main && git pull && git branch -D <branch> 2>/dev/null || true`
- Note: Fast-forward merges auto-delete the local branch, so the delete may
  silently fail (which is fine)

## Documentation Style

- Code examples in docs don't need import statements (we don't show
  `import garth` either)
- Keep examples concise and focused on usage

## API Design Guidelines

- Methods that make API calls should return Pydantic dataclasses of the
  response for consistency
- Use `camel_to_snake_dict()` to transform API responses before passing
  to dataclasses
