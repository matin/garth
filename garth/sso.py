import re
import time
from typing import Optional

from . import http
from .exc import GarthException

CSRF_RE = re.compile(r'name="_csrf"\s+value="(.+?)"')
TITLE_RE = re.compile(r"<title>(.+?)</title>")


def login(
    email: str, password: str, /, client: Optional["http.Client"] = None
) -> dict:
    client = client or http.client

    # Define params based on domain
    SSO = f"https://sso.{client.domain}/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = dict(
        id="gauth-widget",
        embedWidget="true",
        gauthHost=SSO,
    )
    SIGNIN_PARAMS = dict(
        id="gauth-widget",
        service=SSO_EMBED,
        source=SSO_EMBED,
        redirectAfterAccountLoginUrl=SSO_EMBED,
        redirectAfterAccountCreationUrl=SSO_EMBED,
        gauthHost=SSO_EMBED,
    )

    # Set cookies
    client.get("sso", "/sso/embed", params=SSO_EMBED_PARAMS)

    # Get CSRF token
    client.get(
        "sso",
        "/sso/signin",
        params=SIGNIN_PARAMS,
        referrer=True,
    )
    csrf_token = get_csrf_token(client.last_resp.text)

    # Submit login form with email and password
    client.post(
        "sso",
        "/sso/signin",
        params=SIGNIN_PARAMS,
        referrer=True,
        data=dict(
            username=email,
            password=password,
            embed="true",
            _csrf=csrf_token,
        ),
    )
    title = get_title(client.last_resp.text)

    # Handle MFA
    if "MFA" in title:
        handle_mfa(client, SIGNIN_PARAMS)

    assert get_title(client.last_resp.text) == "Success"

    # Parse ticket
    m = re.search(r'embed\?ticket=([^"]+)"', client.last_resp.text)
    assert m
    ticket = m.group(1)

    # Exchange SSO Ticket for Connect Token
    client.get(
        "connect",
        "/modern",
        params=dict(ticket=ticket),
        referrer=True,
    )
    token = exchange(client)

    return token


def handle_mfa(client: "http.Client", signin_params: dict) -> None:
    csrf_token = get_csrf_token(client.last_resp.text)
    mfa_code = input("Enter MFA code: ")
    client.post(
        "sso",
        "/sso/verifyMFA/loginEnterMfaCode",
        params=signin_params | dict(rememberMyBrowserChecked="true"),
        referrer=True,
        data={
            "mfa-code": mfa_code,
            "embed": "true",
            "_csrf": csrf_token,
            "fromPage": "setupEnterMfaCode",
        },
    )


def exchange(client: Optional["http.Client"] = None) -> dict:
    client = client or http.client
    token = client.post(
        "connect",
        "/modern/di-oauth/exchange",
        referrer=f"https://connect.{client.domain}/modern",
    ).json()
    return set_expirations(token)


def refresh(
    refresh_token: str, /, client: Optional["http.Client"] = None
) -> dict:
    client = client or http.client

    token = client.post(
        "connect",
        "/services/auth/token/refresh",
        json=dict(refresh_token=refresh_token),
    ).json()
    return set_expirations(token)


def set_expirations(token: dict) -> dict:
    token["expires_at"] = int(time.time() + token["expires_in"])
    token["refresh_token_expires_at"] = int(
        time.time() + token["refresh_token_expires_in"]
    )
    return token


def get_csrf_token(html: str) -> str:
    m = CSRF_RE.search(html)
    if not m:
        raise GarthException("Couldn't find CSRF token")
    return m.group(1)


def get_title(html: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        raise GarthException("Couldn't find title")
    return m.group(1)
