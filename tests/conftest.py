import json
import os
import re
import time

import pytest
from requests import Session

from garth.auth_token import AuthToken
from garth.http import Client


@pytest.fixture
def session():
    return Session()


@pytest.fixture
def client(session) -> Client:
    return Client(session=session)


@pytest.fixture
def auth_token_dict() -> dict:
    return dict(
        scope="CONNECT_READ CONNECT_WRITE",
        jti="foo",
        token_type="Bearer",
        access_token="bar",
        refresh_token="baz",
        expires_in=3599,
        refresh_token_expires_in=7199,
        username="mtamizi",
    )


@pytest.fixture
def auth_token(auth_token_dict: dict) -> AuthToken:
    token = AuthToken(
        expires_at=int(time.time() + 3599),
        refresh_token_expires_at=int(time.time() + 7199),
        **auth_token_dict,
    )
    return token


@pytest.fixture
def authed_client(auth_token: AuthToken) -> Client:
    client = Client()
    try:
        client.load(os.environ["GARTH_SESSION"])
    except KeyError:
        client.auth_token = auth_token
    return client


@pytest.fixture
def vcr(vcr):
    if "GARTH_SESSION" not in os.environ:
        vcr.record_mode = "none"
    return vcr


def sanitize_cookie(cookie_value) -> str:
    return re.sub(r"=[^;]*", "=SANITIZED", cookie_value)


def sanitize_request(request):
    if request.body:
        body = request.body.decode("utf8")
        for key in ["username", "password", "refresh_token"]:
            body = re.sub(key + r"=[^&]*", "username=SANITIZED", body)
        request.body = body.encode("utf8")

    if "Cookie" in request.headers:
        cookies = request.headers["Cookie"].split("; ")
        sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
        request.headers["Cookie"] = "; ".join(sanitized_cookies)
    return request


def sanitize_response(response):
    for key in ["set-cookie", "Set-Cookie"]:
        if key in response["headers"]:
            cookies = response["headers"][key]
            sanitized_cookies = [sanitize_cookie(cookie) for cookie in cookies]
            response["headers"][key] = sanitized_cookies

    if "body" in response and response["body"]["string"]:
        try:
            body = response["body"]["string"].decode("utf8")
            body_json = json.loads(body)
        except json.JSONDecodeError:
            pass
        else:
            # sanitize access_token and refresh_token
            if "access_token" in body_json:
                body_json["access_token"] = "SANITIZED"
            if "refresh_token" in body_json:
                body_json["refresh_token"] = "SANITIZED"
            if "jti" in body_json:
                body_json["jti"] = "SANITIZED"

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
