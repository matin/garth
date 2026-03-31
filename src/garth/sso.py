from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from . import http
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthException

log = logging.getLogger(__name__)

DEFAULT_SESSION_DIR = Path.home() / ".garth"

# Browser state — module-level singleton.
# Limitation: only one active session at a time. This matches garth's
# existing singleton pattern (garth.client). Multi-account use requires
# separate Python processes.
_cm = None  # Camoufox context manager
_browser = None
_page = None
_csrf = None

# Sentinel value used to identify browser-backed placeholder tokens.
# When tokens contain this value, they cannot be used without a browser.
BROWSER_TOKEN_SENTINEL = "browser_session"


def _placeholder_oauth2() -> OAuth2Token:
    """Create a placeholder OAuth2 token for browser-backed sessions.

    The browser session handles real auth via cookies. These tokens
    exist only to satisfy garth's Client interface which expects
    OAuth tokens to be set after login.
    """
    return OAuth2Token(
        scope="readwrite",
        jti=BROWSER_TOKEN_SENTINEL,
        token_type="Bearer",
        access_token=BROWSER_TOKEN_SENTINEL,
        refresh_token=BROWSER_TOKEN_SENTINEL,
        expires_in=86400 * 365,
        expires_at=int(time.time()) + 86400 * 365,
        refresh_token_expires_in=86400 * 365,
        refresh_token_expires_at=int(time.time()) + 86400 * 365,
    )


def login(
    email: str,
    password: str,
    /,
    client: http.Client | None = None,
    prompt_mfa: Callable | None = lambda: input("MFA code: "),
    return_on_mfa: bool = False,
    session_dir: str | Path | None = None,
    headless: bool = True,
) -> (
    tuple[OAuth1Token, OAuth2Token]
    | tuple[Literal["needs_mfa"], dict[str, Any]]
):
    """Login to Garmin Connect via browser automation.

    Uses Camoufox (headless Firefox) to perform SSO login, bypassing
    Cloudflare bot detection that blocks all Python HTTP clients.

    Note:
        This is not thread-safe. Playwright browser pages cannot be
        shared across threads. Use one Client per thread if needed.

    Args:
        email: Garmin account email
        password: Garmin account password
        client: garth Client instance (used for domain config)
        prompt_mfa: Callable that returns MFA code when prompted
        return_on_mfa: Not supported with browser login. Raises
            NotImplementedError if True.
        session_dir: Directory to store browser session cookies
        headless: Run browser without visible window (default: True)
    """
    global _cm, _browser, _page, _csrf

    if return_on_mfa:
        raise NotImplementedError(
            "return_on_mfa is not supported with browser-based login. "
            "MFA is handled interactively via the prompt_mfa callback."
        )

    client = client or http.client
    session_dir = Path(session_dir) if session_dir else DEFAULT_SESSION_DIR
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "browser_session.json"

    # Close any existing browser before launching a new one
    close()

    # Launch browser via context manager
    from camoufox.sync_api import Camoufox

    _cm = Camoufox(headless=headless)
    _browser = _cm.__enter__()
    _page = _browser.new_page()
    context = _page.context

    # Load saved session cookies
    if session_file.exists():
        try:
            session = json.loads(session_file.read_text())
            age_days = (
                time.time() - session.get("saved_at", 0)
            ) / 86400
            if age_days < 364 and session.get("cookies"):
                context.add_cookies(session["cookies"])
                log.info(
                    "Loaded session cookies (%.0f days old)", age_days
                )
        except Exception as e:
            log.debug("Could not load session cookies: %s", e)

    # Navigate to Garmin Connect
    try:
        _page.goto(
            "https://connect.garmin.com/modern/",
            wait_until="domcontentloaded",
            timeout=30000,
        )
    except Exception as e:
        log.debug("Initial navigation error (may be expected): %s", e)
    time.sleep(3)

    # Check if session is valid
    url = _page.url
    needs_login = "sso.garmin.com" in url or not _try_setup()

    if needs_login:
        _do_login(email, password, prompt_mfa, client.domain)
        _save_session(session_file)

    # Return placeholder tokens — the browser session handles auth
    oauth1 = OAuth1Token(
        oauth_token=BROWSER_TOKEN_SENTINEL,
        oauth_token_secret=BROWSER_TOKEN_SENTINEL,
        domain=client.domain,
    )
    oauth2 = _placeholder_oauth2()

    return oauth1, oauth2


def exchange(
    oauth1: OAuth1Token,
    client: http.Client,
    *,
    login: bool = False,
) -> OAuth2Token:
    """Refresh OAuth2 token — no-op with browser transport.

    The browser session handles auth via cookies, so token refresh
    is not needed. Returns a fresh placeholder token.
    """
    return _placeholder_oauth2()


def handle_mfa(
    client: http.Client,
    login_params: dict,
    prompt_mfa: Callable,
    *,
    mfa_method: str = "email",
) -> str:
    """Not used with browser transport — MFA is handled in-browser."""
    raise NotImplementedError(
        "MFA is handled by the browser login flow"
    )


def resume_login(
    client_state: dict, mfa_code: str
) -> tuple[OAuth1Token, OAuth2Token]:
    """Not used with browser transport — MFA is handled in-browser."""
    raise NotImplementedError(
        "MFA is handled by the browser login flow"
    )


def set_expirations(token: dict) -> dict:
    token["expires_at"] = int(time.time() + token["expires_in"])
    token["refresh_token_expires_at"] = int(
        time.time() + token["refresh_token_expires_in"]
    )
    return token


def is_browser_token(token: OAuth1Token | OAuth2Token | None) -> bool:
    """Check if a token is a browser-backed placeholder."""
    if token is None:
        return False
    if isinstance(token, OAuth1Token):
        return token.oauth_token == BROWSER_TOKEN_SENTINEL
    if isinstance(token, OAuth2Token):
        return token.access_token == BROWSER_TOKEN_SENTINEL
    return False


def get_page():
    """Get the browser page for use by Client.request()."""
    return _page


def get_csrf():
    """Get the CSRF token for use by Client.request()."""
    return _csrf


def close() -> None:
    """Close the browser. Call when done."""
    global _cm, _browser, _page, _csrf
    if _cm:
        try:
            _cm.__exit__(None, None, None)
        except Exception as e:
            log.debug("Error closing browser context manager: %s", e)
    _cm = None
    _browser = None
    _page = None
    _csrf = None


# --- Internal helpers ---


def _try_setup() -> bool:
    """Extract CSRF token and verify session is valid."""
    global _csrf
    current = _page.url
    if "/modern/" not in current:
        try:
            _page.goto(
                "https://connect.garmin.com/modern/",
                wait_until="domcontentloaded",
            )
        except Exception as e:
            log.debug("Navigation to /modern/ failed: %s", e)
        time.sleep(3)

    try:
        setup = _page.evaluate("""
            async () => {
                const csrf = document.querySelector(
                    'meta[name="csrf-token"], meta[name="_csrf"]'
                )?.content;
                const h = {'connect-csrf-token': csrf};
                const resp = await fetch(
                    '/gc-api/userprofile-service/socialProfile',
                    {credentials: 'include', headers: h}
                );
                const profile = resp.status === 200
                    ? await resp.json() : null;
                return {
                    csrf,
                    displayName: profile?.displayName,
                };
            }
        """)
        _csrf = setup.get("csrf")
        return bool(_csrf)
    except Exception as e:
        log.debug("CSRF extraction failed: %s", e)
        return False


def _do_login(
    email: str,
    password: str,
    prompt_mfa: Callable | None,
    domain: str = "garmin.com",
) -> None:
    """Perform SSO login via browser."""
    global _page, _csrf

    # Build SSO URL from domain config (supports garmin.cn)
    sso_domain = "sso.garmin.com"
    connect_domain = "connect.garmin.com"
    if domain == "garmin.cn":
        sso_domain = "sso.garmin.cn"
        connect_domain = "connect.garmin.cn"

    sso_url = (
        f"https://{sso_domain}/portal/sso/en-US/sign-in"
        f"?clientId=GarminConnect"
        f"&service=https%3A%2F%2F{connect_domain}%2Fapp"
    )

    try:
        _page.goto(
            sso_url, wait_until="domcontentloaded", timeout=30000
        )
    except Exception as e:
        log.debug("SSO page navigation error: %s", e)
    time.sleep(3)

    # Fill login form
    email_input = _page.locator('input[name="email"]').first
    email_input.wait_for(timeout=15000)
    email_input.click()
    _page.keyboard.type(email, delay=30)

    _page.locator('input[name="password"]').first.click()
    _page.keyboard.type(password, delay=30)

    try:
        _page.evaluate(
            "() => { const cb = document.querySelector("
            '"input[name=remember]"); '
            "if (cb && !cb.checked) cb.click(); }"
        )
    except Exception as e:
        log.debug("Remember-me checkbox not found: %s", e)

    _page.locator('button[type="submit"]').first.click()

    # Wait for redirect or MFA
    for _ in range(120):
        time.sleep(1)
        url = _page.url

        if (
            connect_domain in url
            and sso_domain not in url
        ):
            break

        # Check tabs (some redirects open new tabs)
        for p in _page.context.pages:
            if (
                connect_domain in p.url
                and sso_domain not in p.url
            ):
                _page = p
                break
        if (
            connect_domain in _page.url
            and sso_domain not in _page.url
        ):
            break

        # MFA detection
        has_mfa = _page.evaluate(
            "() => document.querySelector("
            '"input[name=securityCode]") !== null'
        )
        if has_mfa:
            mfa_func = prompt_mfa or input
            code = mfa_func().strip()

            _page.locator(
                'input[name="securityCode"]'
            ).first.fill(code)
            try:
                _page.evaluate(
                    "() => { const cb = document.querySelector("
                    '"input[name=remember]"); '
                    "if (cb && !cb.checked) cb.click(); }"
                )
            except Exception as e:
                log.debug("MFA remember checkbox not found: %s", e)
            _page.locator('button:has-text("Next")').first.click()

            # Wait for redirect after MFA
            for _ in range(60):
                time.sleep(1)
                if (
                    connect_domain in _page.url
                    and sso_domain not in _page.url
                ):
                    break
                try:
                    has_app = _page.evaluate(
                        "() => document.body?.innerText"
                        '?.includes("Activities")'
                    )
                    if has_app:
                        _page.goto(
                            f"https://{connect_domain}/modern/",
                            wait_until="domcontentloaded",
                        )
                        time.sleep(2)
                        break
                except Exception as e:
                    log.debug("Post-MFA check failed: %s", e)
            break

    time.sleep(3)

    if sso_domain in _page.url:
        raise GarthException(
            msg="Login failed — still on SSO page"
        )

    if not _try_setup():
        raise GarthException(
            msg="Login succeeded but could not extract session data"
        )


def _save_session(session_file: Path) -> None:
    """Save browser cookies for session persistence."""
    try:
        cookies = _page.context.cookies()
        garmin_cookies = [
            c for c in cookies if "garmin" in c.get("domain", "")
        ]
        session = {
            "cookies": garmin_cookies,
            "saved_at": time.time(),
        }
        fd = os.open(
            str(session_file),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600,
        )
        with os.fdopen(fd, "w") as f:
            json.dump(session, f, indent=2)
    except Exception as e:
        log.warning("Could not save session cookies: %s", e)
