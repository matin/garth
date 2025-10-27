import asyncio
import re
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


CSRF_RE = re.compile(r'name="_csrf"\s+value="(.+?)"')
TITLE_RE = re.compile(r"<title>(.+?)</title>")
OAUTH_CONSUMER_URL = "https://thegarth.s3.amazonaws.com/oauth_consumer.json"
OAUTH_CONSUMER: dict[str, str] = {}
USER_AGENT = {"User-Agent": "com.garmin.android.apps.connectmobile"}


class GarminOAuth1Session(OAuth1Session):
    def __init__(
        self,
        /,
        parent: Session | None = None,
        **kwargs,
    ):
        global OAUTH_CONSUMER
        if not OAUTH_CONSUMER:
            OAUTH_CONSUMER = requests.get(OAUTH_CONSUMER_URL).json()
        super().__init__(
            OAUTH_CONSUMER["consumer_key"],
            OAUTH_CONSUMER["consumer_secret"],
            **kwargs,
        )
        if parent is not None:
            self.mount("https://", parent.adapters["https://"])
            self.proxies = parent.proxies
            self.verify = parent.verify


def login(
    email: str,
    password: str,
    /,
    client: "http.Client | None" = None,
    prompt_mfa: Callable | None = lambda: input("MFA code: "),
    return_on_mfa: bool = False,
) -> (
    tuple[OAuth1Token, OAuth2Token]
    | tuple[Literal["needs_mfa"], dict[str, Any]]
):
    """Login to Garmin Connect.

    Args:
        email: Garmin account email
        password: Garmin account password
        client: Optional HTTP client to use
        prompt_mfa: Callable that prompts for MFA code. Returns on MFA if None.
        return_on_mfa: If True, returns dict with MFA info instead of prompting

    Returns:
        If return_on_mfa=False (default):
            Tuple[OAuth1Token, OAuth2Token]: OAuth tokens after login
        If return_on_mfa=True and MFA required:
            dict: Contains needs_mfa and client_state for resume_login()
    """
    client = client or http.client

    # Define params based on domain
    SSO = f"https://sso.{client.domain}/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = dict(
        id="gauth-widget",
        embedWidget="true",
        gauthHost=SSO,
    )
    SIGNIN_PARAMS = {
        **SSO_EMBED_PARAMS,
        **dict(
            gauthHost=SSO_EMBED,
            service=SSO_EMBED,
            source=SSO_EMBED,
            redirectAfterAccountLoginUrl=SSO_EMBED,
            redirectAfterAccountCreationUrl=SSO_EMBED,
        ),
    }

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
        if return_on_mfa or prompt_mfa is None:
            return "needs_mfa", {
                "signin_params": SIGNIN_PARAMS,
                "client": client,
            }

        handle_mfa(client, SIGNIN_PARAMS, prompt_mfa)
        title = get_title(client.last_resp.text)

    if title != "Success":
        raise GarthException(f"Unexpected title: {title}")
    return _complete_login(client)


def get_oauth1_token(ticket: str, client: "http.Client") -> OAuth1Token:
    sess = GarminOAuth1Session(parent=client.sess)
    base_url = f"https://connectapi.{client.domain}/oauth-service/oauth/"
    login_url = f"https://sso.{client.domain}/sso/embed"
    url = (
        f"{base_url}preauthorized?ticket={ticket}&login-url={login_url}"
        "&accepts-mfa-tokens=true"
    )
    resp = sess.get(
        url,
        headers=USER_AGENT,
        timeout=client.timeout,
    )
    resp.raise_for_status()
    parsed = parse_qs(resp.text)
    token = {k: v[0] for k, v in parsed.items()}
    return OAuth1Token(domain=client.domain, **token)  # type: ignore


def exchange(oauth1: OAuth1Token, client: "http.Client") -> OAuth2Token:
    sess = GarminOAuth1Session(
        resource_owner_key=oauth1.oauth_token,
        resource_owner_secret=oauth1.oauth_token_secret,
        parent=client.sess,
    )
    data = dict(mfa_token=oauth1.mfa_token) if oauth1.mfa_token else {}
    base_url = f"https://connectapi.{client.domain}/oauth-service/oauth/"
    url = f"{base_url}exchange/user/2.0"
    headers = {
        **USER_AGENT,
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
    client: "http.Client", signin_params: dict, prompt_mfa: Callable
) -> None:
    csrf_token = get_csrf_token(client.last_resp.text)
    if asyncio.iscoroutinefunction(prompt_mfa):
        mfa_code = asyncio.run(prompt_mfa())
    else:
        mfa_code = prompt_mfa()
    client.post(
        "sso",
        "/sso/verifyMFA/loginEnterMfaCode",
        params=signin_params,
        referrer=True,
        data={
            "mfa-code": mfa_code,
            "embed": "true",
            "_csrf": csrf_token,
            "fromPage": "setupEnterMfaCode",
        },
    )


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


def resume_login(
    client_state: dict, mfa_code: str
) -> tuple[OAuth1Token, OAuth2Token]:
    """Complete login after MFA code is provided.

    Args:
        client_state: The client state from login() when MFA was needed
        mfa_code: The MFA code provided by the user

    Returns:
        Tuple[OAuth1Token, OAuth2Token]: The OAuth tokens after login
    """
    client = client_state["client"]
    signin_params = client_state["signin_params"]
    handle_mfa(client, signin_params, lambda: mfa_code)
    return _complete_login(client)


def _complete_login(client: "http.Client") -> tuple[OAuth1Token, OAuth2Token]:
    """Complete the login process after successful authentication.

    Args:
        client: The HTTP client

    Returns:
        Tuple[OAuth1Token, OAuth2Token]: The OAuth tokens
    """
    # Parse ticket
    m = re.search(r'embed\?ticket=([^"]+)"', client.last_resp.text)
    if not m:
        raise GarthException(
            "Couldn't find ticket in response"
        )  # pragma: no cover
    ticket = m.group(1)

    oauth1 = get_oauth1_token(ticket, client)
    oauth2 = exchange(oauth1, client)

    return oauth1, oauth2
