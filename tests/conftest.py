import gzip
import io
import os
import threading
import time
import types
from urllib.parse import urlencode

import pytest
import yaml

from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.http import Client, _Response
from garth.telemetry import REDACTED, sanitize, sanitize_cookie


# Disable telemetry before tests
os.environ["GARTH_TELEMETRY_ENABLED"] = "false"


def pytest_configure(config):
    """Register the vcr marker so tests don't emit warnings."""
    config.addinivalue_line(
        "markers",
        "vcr: replay API responses from cassette YAML files",
    )


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Prevent env leaks from affecting tests."""
    monkeypatch.setenv("GARTH_TELEMETRY_ENABLED", "false")
    monkeypatch.delenv("GARTH_HOME", raising=False)
    monkeypatch.delenv("GARTH_TOKEN", raising=False)


@pytest.fixture
def client(monkeypatch) -> Client:
    monkeypatch.delenv("GARTH_HOME", raising=False)
    monkeypatch.delenv("GARTH_TOKEN", raising=False)
    return Client()


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
    return OAuth2Token(
        expires_at=int(time.time() + 3599),
        refresh_token_expires_at=int(time.time() + 7199),
        **oauth2_token_dict,
    )


# --- Cassette replay infrastructure ---


def _load_cassette_interactions(cassette_dir, test_name):
    """Load interactions from a VCR cassette YAML file."""
    yaml_path = os.path.join(cassette_dir, f"{test_name}.yaml")
    if not os.path.exists(yaml_path):
        return None
    with open(yaml_path) as f:
        cassette = yaml.safe_load(f)
    return cassette.get("interactions", [])


def _make_cassette_replayer(interactions):
    """Create a request() method that replays cassette responses.

    Matches by URL path and method. For duplicate URLs, serves
    in order. Thread-safe for parallel calls from
    ThreadPoolExecutor.
    """
    remaining = list(interactions)
    lock = threading.Lock()

    def mock_request(
        self,
        method,
        subdomain,
        path,
        /,
        api=False,
        referrer=False,
        headers=None,
        **kwargs,
    ):
        if headers is None:
            headers = {}
        match_path = path.lstrip("/")
        params = kwargs.get("params")
        if params:
            match_path += "?" + urlencode(params, doseq=True)

        with lock:
            best_idx = None
            for i, interaction in enumerate(remaining):
                req = interaction["request"]
                cassette_uri = req.get("uri", "")
                cassette_method = req.get("method", "GET")

                if (
                    method.upper() == cassette_method.upper()
                    and match_path in cassette_uri
                ):
                    best_idx = i
                    break

            if best_idx is None:
                expected = f"{method.upper()} {match_path}"
                available = [
                    f"{r['request'].get('method', 'GET')} "
                    f"{r['request'].get('uri', '')}"
                    for r in remaining
                ]
                raise RuntimeError(
                    f"No cassette match for {expected}. "
                    f"Available: {available}"
                )

            interaction = remaining.pop(best_idx)

        resp_data = interaction["response"]
        status = resp_data.get("status", {}).get("code", 200)
        body = resp_data.get("body", {}).get("string", "")
        if isinstance(body, bytes):
            try:
                body = gzip.GzipFile(
                    fileobj=io.BytesIO(body)
                ).read().decode("utf-8")
            except (gzip.BadGzipFile, OSError):
                body = body.decode("utf-8", errors="replace")
        uri = interaction["request"].get("uri", "")

        resp = _Response(status, body, uri)
        self.last_resp = resp

        if not resp.ok:
            resp.raise_for_status()

        return resp

    return mock_request


def _find_cassette_dir(test_file):
    """Find the cassette directory relative to a test file."""
    test_dir = os.path.dirname(str(test_file))
    cassette_dir = os.path.join(test_dir, "cassettes")
    if os.path.isdir(cassette_dir):
        return cassette_dir
    return None


@pytest.fixture
def authed_client(
    request,
    oauth1_token: OAuth1Token,
    oauth2_token: OAuth2Token,
) -> Client:
    """Client with tokens and cassette replay for vcr tests."""
    c = Client()
    c.configure(
        oauth1_token=oauth1_token, oauth2_token=oauth2_token
    )
    c._garth_home = None
    assert c.oauth2_token and isinstance(
        c.oauth2_token, OAuth2Token
    )
    assert not c.oauth2_token.expired

    marker = request.node.get_closest_marker("vcr")
    if marker:
        cassette_dir = _find_cassette_dir(request.fspath)
        if cassette_dir:
            test_name = request.node.name
            interactions = _load_cassette_interactions(
                cassette_dir, test_name
            )
            if interactions:
                c.request = types.MethodType(
                    _make_cassette_replayer(interactions), c
                )

    return c
