import gzip
import io
import json
import os
import re
import time

import pytest
from requests import Session

from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.http import Client


@pytest.fixture
def session():
    return Session()


@pytest.fixture
def client(session) -> Client:
    return Client(session=session)


@pytest.fixture
def oauth1_token_dict() -> dict:
    return dict(
        oauth_token="7fdff19aa9d64dda83e9d7858473aed1",
        oauth_token_secret="49919d7c4c8241ac93fb4345886fbcea",
        mfa_token="ab316f8640f3491f999f3298f3d6f1bb",
        mfa_expiration_timestamp="2024-08-02 05:56:10.000",
        domain="garmin.com",
    )


@pytest.fixture
def oauth1_token(oauth1_token_dict) -> OAuth1Token:
    return OAuth1Token(**oauth1_token_dict)


@pytest.fixture
def oauth2_token_dict() -> dict:
    return dict(
        scope="CONNECT_READ CONNECT_WRITE",
        jti="foo",
        token_type="Bearer",
        access_token="bar",
        refresh_token="baz",
        expires_in=3599,
        refresh_token_expires_in=7199,
    )


@pytest.fixture
def oauth2_token(oauth2_token_dict: dict) -> OAuth2Token:
    token = OAuth2Token(
        expires_at=int(time.time() + 3599),
        refresh_token_expires_at=int(time.time() + 7199),
        **oauth2_token_dict,
    )
    return token


@pytest.fixture
def authed_client(
    oauth1_token: OAuth1Token, oauth2_token: OAuth2Token
) -> Client:
    client = Client()
    try:
        client.load(os.environ["GARTH_HOME"])
    except KeyError:
        client.configure(oauth1_token=oauth1_token, oauth2_token=oauth2_token)
    assert client.oauth2_token and isinstance(client.oauth2_token, OAuth2Token)
    assert not client.oauth2_token.expired
    return client


@pytest.fixture
def vcr(vcr):
    if "GARTH_HOME" not in os.environ:
        vcr.record_mode = "none"
    return vcr


def sanitize_cookie(cookie_value) -> str:
    return re.sub(r"=[^;]*", "=SANITIZED", cookie_value)


def sanitize_request(request):
    if request.body:
        try:
            body = request.body.decode("utf8")
        except UnicodeDecodeError:
            ...
        else:
            for key in ["username", "password", "refresh_token"]:
                body = re.sub(key + r"=[^&]*", f"{key}=SANITIZED", body)
            request.body = body.encode("utf8")

    if "Cookie" in request.headers:
        cookies = request.headers["Cookie"].split("; ")
        sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
        request.headers["Cookie"] = "; ".join(sanitized_cookies)
    return request


def sanitize_response(response):
    try:
        encoding = response["headers"].pop("Content-Encoding")
    except KeyError:
        ...
    else:
        if encoding[0] == "gzip":
            body = response["body"]["string"]
            buffer = io.BytesIO(body)
            try:
                body = gzip.GzipFile(fileobj=buffer).read()
            except gzip.BadGzipFile:  # pragma: no cover
                ...
            else:
                response["body"]["string"] = body

    for key in ["set-cookie", "Set-Cookie"]:
        if key in response["headers"]:
            cookies = response["headers"][key]
            sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
            response["headers"][key] = sanitized_cookies

    try:
        body = response["body"]["string"].decode("utf8")
    except UnicodeDecodeError:
        pass
    else:
        patterns = [
            "oauth_token=[^&]*",
            "oauth_token_secret=[^&]*",
            "mfa_token=[^&]*",
        ]
        for pattern in patterns:
            body = re.sub(pattern, pattern.split("=")[0] + "=SANITIZED", body)
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            pass
        else:
            if body_json and isinstance(body_json, dict):
                for field in [
                    "access_token",
                    "refresh_token",
                    "jti",
                    "consumer_key",
                    "consumer_secret",
                ]:
                    if field in body_json:
                        body_json[field] = "SANITIZED"

            body = json.dumps(body_json)
        response["body"]["string"] = body.encode("utf8")

    return response


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "Bearer SANITIZED")],
        "before_record_request": sanitize_request,
        "before_record_response": sanitize_response,
    }
