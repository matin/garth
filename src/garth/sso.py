from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Callable
from typing import Any, Literal
from urllib.parse import parse_qs

import requests
from requests import Session
from requests_oauthlib import OAuth1Session

from . import http
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthException


CLIENT_ID = "GCM_IOS_DARK"
OAUTH_CONSUMER_URL = "https://thegarth.s3.amazonaws.com/oauth_consumer.json"
OAUTH_CONSUMER: dict[str, str] = {}

SSO_SUCCESSFUL = "SUCCESSFUL"
SSO_MFA_REQUIRED = "MFA_REQUIRED"

# Android user agent — must match the Android consumer key from S3
OAUTH_USER_AGENT = {"User-Agent": "com.garmin.android.apps.connectmobile"}

# Browser-like headers for SSO to avoid Cloudflare challenges.
# The SSO endpoints run in a WebView, so requests must look like a
# browser — not a Python HTTP client.
_SSO_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
)
SSO_PAGE_HEADERS = {
    "User-Agent": _SSO_UA,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
}


class GarminOAuth1Session(OAuth1Session):
    def __init__(
        self,
        /,
        parent: Session | None = None,
        **kwargs,
    ):
        global OAUTH_CONSUMER
        if not OAUTH_CONSUMER:
            request_kwargs: dict[str, Any] = {}
            if parent is not None:
                request_kwargs["proxies"] = parent.proxies
                request_kwargs["verify"] = parent.verify
            OAUTH_CONSUMER = requests.get(
                OAUTH_CONSUMER_URL, **request_kwargs
            ).json()
        super().__init__(
            OAUTH_CONSUMER["consumer_key"],
            OAUTH_CONSUMER["consumer_secret"],
            **kwargs,
        )
        if parent is not None:
            self.mount("https://", parent.adapters["https://"])
            self.cookies.update(parent.cookies)
            self.proxies = parent.proxies
            self.verify = parent.verify
            self.hooks["response"].extend(parent.hooks["response"])


def _parse_sso_response(
    resp_json: dict[str, Any],
    expected_type: str | None = None,
) -> dict[str, Any]:
    status = resp_json.get("responseStatus", {})
    resp_type = status.get("type", "UNKNOWN")
    message = status.get("message", "")
    if expected_type and resp_type != expected_type:
        detail = f"{resp_type}: {message}" if message else resp_type
        raise GarthException(msg=f"SSO error: {detail}")
    return resp_json


def login(
    email: str,
    password: str,
    /,
    client: http.Client | None = None,
    prompt_mfa: Callable | None = lambda: input("MFA code: "),
    return_on_mfa: bool = False,
) -> (
    tuple[OAuth1Token, OAuth2Token]
    | tuple[Literal["needs_mfa"], dict[str, Any]]
):
    client = client or http.client
    service_url = f"https://mobile.integration.{client.domain}/gcm/ios"
    login_params = {
        "clientId": CLIENT_ID,
        "locale": "en-US",
        "service": service_url,
    }

    # Set cookies
    client.get(
        "sso",
        "/mobile/sso/en/sign-in",
        params={"clientId": CLIENT_ID},
        headers={**SSO_PAGE_HEADERS, "Sec-Fetch-Site": "none"},
    )

    # Submit login
    client.post(
        "sso",
        "/mobile/api/login",
        params=login_params,
        json={
            "username": email,
            "password": password,
            "rememberMe": False,
            "captchaToken": "",
        },
    )
    resp_json = client.last_resp.json()
    resp_type = resp_json.get("responseStatus", {}).get("type")

    if resp_type == SSO_SUCCESSFUL:
        ticket = resp_json["serviceTicketId"]
        return _complete_login(ticket, client)

    if resp_type == SSO_MFA_REQUIRED:
        if return_on_mfa or prompt_mfa is None:
            return "needs_mfa", {
                "login_params": login_params,
                "client": client,
            }
        ticket = handle_mfa(client, login_params, prompt_mfa)
        return _complete_login(ticket, client)

    _parse_sso_response(resp_json, SSO_SUCCESSFUL)
    raise GarthException(msg="Unexpected SSO response")  # pragma: no cover


def get_oauth1_token(ticket: str, client: http.Client) -> OAuth1Token:
    sess = GarminOAuth1Session(parent=client.sess)
    base_url = f"https://connectapi.{client.domain}/oauth-service/oauth/"
    login_url = f"https://mobile.integration.{client.domain}/gcm/ios"
    url = (
        f"{base_url}preauthorized?ticket={ticket}&login-url={login_url}"
        "&accepts-mfa-tokens=true"
    )
    resp = sess.get(
        url,
        headers=OAUTH_USER_AGENT,
        timeout=client.timeout,
    )
    resp.raise_for_status()
    parsed = parse_qs(resp.text)
    token = {k: v[0] for k, v in parsed.items()}
    return OAuth1Token(domain=client.domain, **token)  # type: ignore


def exchange(
    oauth1: OAuth1Token,
    client: http.Client,
    *,
    login: bool = False,
) -> OAuth2Token:
    sess = GarminOAuth1Session(
        resource_owner_key=oauth1.oauth_token,
        resource_owner_secret=oauth1.oauth_token_secret,
        parent=client.sess,
    )
    data: dict[str, str] = {}
    if login:
        data["audience"] = "GARMIN_CONNECT_MOBILE_IOS_DI"
    if oauth1.mfa_token:
        data["mfa_token"] = oauth1.mfa_token
    base_url = f"https://connectapi.{client.domain}/oauth-service/oauth/"
    url = f"{base_url}exchange/user/2.0"
    headers = {
        **OAUTH_USER_AGENT,
        **{"Content-Type": "application/x-www-form-urlencoded"},
    }
    resp = sess.post(
        url,
        headers=headers,
        data=data,
        timeout=client.timeout,
    )
    resp.raise_for_status()
    token = resp.json()
    return OAuth2Token(**set_expirations(token))


def handle_mfa(
    client: http.Client, login_params: dict, prompt_mfa: Callable
) -> str:
    if inspect.iscoroutinefunction(prompt_mfa):
        mfa_code = asyncio.run(prompt_mfa())
    else:
        mfa_code = prompt_mfa()
    client.post(
        "sso",
        "/mobile/api/mfa/verifyCode",
        params=login_params,
        json={
            "mfaMethod": "email",
            "mfaVerificationCode": mfa_code,
            "rememberMyBrowser": False,
            "reconsentList": [],
            "mfaSetup": False,
        },
    )
    resp_json = _parse_sso_response(client.last_resp.json(), SSO_SUCCESSFUL)
    return resp_json["serviceTicketId"]


def set_expirations(token: dict) -> dict:
    token["expires_at"] = int(time.time() + token["expires_in"])
    token["refresh_token_expires_at"] = int(
        time.time() + token["refresh_token_expires_in"]
    )
    return token


def resume_login(
    client_state: dict, mfa_code: str
) -> tuple[OAuth1Token, OAuth2Token]:
    client = client_state["client"]
    login_params = client_state["login_params"]
    ticket = handle_mfa(client, login_params, lambda: mfa_code)
    return _complete_login(ticket, client)


def _complete_login(
    ticket: str, client: http.Client
) -> tuple[OAuth1Token, OAuth2Token]:
    # Sets Cloudflare LB cookie for backend pinning — best-effort
    try:
        client.get(
            "sso",
            "/portal/sso/embed",
            headers={**SSO_PAGE_HEADERS, "Sec-Fetch-Site": "same-origin"},
            referrer=True,
        )
    except GarthException:  # pragma: no cover
        pass

    oauth1 = get_oauth1_token(ticket, client)
    oauth2 = exchange(oauth1, client, login=True)
    return oauth1, oauth2
