import re
import time
from typing import Optional
from urllib.parse import urlencode

from . import http


def login(
    email: str, password: str, /, client: Optional["http.Client"] = None
) -> tuple[dict, str]:
    client = client or http.client

    # Define params based on domain
    SSO = f"https://sso.{client.domain}/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = [
        ("id", "gauth-widget"),
        ("embedWidget", "true"),
        ("gauthHost", SSO),
    ]
    SIGNIN_PARAMS = [
        ("id", "gauth-widget"),
        ("service", SSO_EMBED),
        ("source", SSO_EMBED),
        ("redirectAfterAccountLoginUrl", SSO_EMBED),
        ("redirectAfterAccountCreationUrl", SSO_EMBED),
        ("gauthHost", SSO_EMBED),
    ]
    SIGNIN_URL = f"{SSO}/signin?{urlencode(SIGNIN_PARAMS)}"

    # Set cookies
    client.get("sso", "/sso/embed", params=SSO_EMBED_PARAMS)

    # Get CSRF token
    resp = client.get("sso", "/sso/signin", params=SIGNIN_PARAMS)
    m = re.search(r'name="_csrf" value="(.+?)"', resp.text)
    if not m:
        raise Exception("Could not find CSRF token")
    csrf_token = m.group(1)

    # Sign in
    data = dict(
        username=email,
        password=password,
        embed="true",
        _csrf=csrf_token,
    )
    resp = client.post(
        "sso",
        "/sso/signin",
        params=SIGNIN_PARAMS,
        data=data,
        headers=dict(Referer=SIGNIN_URL),
    )
    m = re.search(r"<title>(.+?)</title>", resp.text)
    if not (m and m.group(1) == "Success"):
        raise Exception("Login failed")

    # Parse ticket
    m = re.search(r'embed\?ticket=([^"]+)"', resp.text)
    if not m:
        raise Exception("Could not find Service Ticket")
    ticket = m.group(1)

    # Get username
    resp = client.get("connect", "/modern", params=dict(ticket=ticket))
    m = re.search(r'userName":"(.+?)"', resp.text)
    if not m:
        raise Exception("Could not find username")
    username = m.group(1)

    # Create oauth exchange token
    token = exchange(client)

    return token, username


def exchange(client: Optional["http.Client"] = None) -> dict:
    client = client or http.client
    token = client.post("connect", "/modern/di-oauth/exchange").json()
    return _set_expirations(token)


def refresh(
    refresh_token: str, /, client: Optional["http.Client"] = None
) -> dict:
    client = client or http.client

    token = client.post(
        "connect",
        "/services/auth/token/refresh",
        json=dict(refresh_token=refresh_token),
    ).json()
    return _set_expirations(token)


def _set_expirations(token: dict) -> dict:
    token["expires_at"] = int(time.time() + token["expires_in"])
    token["refresh_token_expires_at"] = int(
        time.time() + token["refresh_token_expires_in"]
    )
    return token
