import re
import time
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs

import requests
from requests_oauthlib import OAuth1Session

from . import http
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthException

CSRF_RE = re.compile(r'name="_csrf"\s+value="(.+?)"')
TITLE_RE = re.compile(r"<title>(.+?)</title>")
OAUTH_CONSUMER_URL = "https://thegarth.s3.amazonaws.com/oauth_consumer.json"
OAUTH_CONSUMER: Dict[str, str] = {}
USER_AGENT = {"User-Agent": "com.garmin.android.apps.connectmobile"}


class GarminOAuth1Session(OAuth1Session):
    def __init__(self, **kwargs):
        global OAUTH_CONSUMER
        if not OAUTH_CONSUMER:
            OAUTH_CONSUMER = requests.get(OAUTH_CONSUMER_URL).json()
        super().__init__(
            OAUTH_CONSUMER["consumer_key"],
            OAUTH_CONSUMER["consumer_secret"],
            **kwargs,
        )


def login(
    email: str, password: str, /, client: Optional["http.Client"] = None
) -> Tuple[OAuth1Token, OAuth2Token]:
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
        handle_mfa(client, SIGNIN_PARAMS)
        title = get_title(client.last_resp.text)

    assert title == "Success"

    # Parse ticket
    m = re.search(r'embed\?ticket=([^"]+)"', client.last_resp.text)
    assert m
    ticket = m.group(1)

    oauth1 = get_oauth1_token(ticket, client)
    oauth2 = exchange(oauth1, client)

    return oauth1, oauth2


def get_oauth1_token(ticket: str, client: "http.Client") -> OAuth1Token:
    sess = GarminOAuth1Session()
    resp = sess.get(
        f"https://connectapi.{client.domain}/oauth-service/oauth/"
        f"preauthorized?ticket={ticket}&login-url="
        f"https://sso.{client.domain}/sso/embed&accepts-mfa-tokens=true",
        headers=USER_AGENT,
    )
    resp.raise_for_status()
    parsed = parse_qs(resp.text)
    token = {k: v[0] for k, v in parsed.items()}
    return OAuth1Token(**token)  # type: ignore


def exchange(oauth1: OAuth1Token, client: "http.Client") -> OAuth2Token:
    sess = GarminOAuth1Session(
        resource_owner_key=oauth1.oauth_token,
        resource_owner_secret=oauth1.oauth_token_secret,
    )
    data = dict(mfa_token=oauth1.mfa_token) if oauth1.mfa_token else {}
    token = sess.post(
        f"https://connectapi.{client.domain}/oauth-service/oauth/exchange/user/2.0",
        headers={
            **USER_AGENT,
            **{"Content-Type": "application/x-www-form-urlencoded"},
        },
        data=data,
    ).json()

    return OAuth2Token(**set_expirations(token))


def handle_mfa(client: "http.Client", signin_params: dict) -> None:
    csrf_token = get_csrf_token(client.last_resp.text)
    mfa_code = input("Enter MFA code: ")
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
