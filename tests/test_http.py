import tempfile
import time

import pytest

from garth.auth_tokens import OAuth2Token
from garth.exc import GarthHTTPError
from garth.http import Client


def test_dump_and_load(authed_client: Client):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)

        new_client = Client()
        new_client.load(tempdir)

        assert new_client.oauth1_token == authed_client.oauth1_token
        assert new_client.oauth2_token == authed_client.oauth2_token


def test_configure_oauth2_token(client: Client, oauth2_token: OAuth2Token):
    assert client.oauth2_token is None
    client.configure(oauth2_token=oauth2_token)
    assert client.oauth2_token == oauth2_token


def test_configure_domain(client: Client):
    assert client.domain == "garmin.com"
    client.configure(domain="garmin.cn")
    assert client.domain == "garmin.cn"


def test_configure_proxies(client: Client):
    assert client.sess.proxies == {}
    proxy = {"https": "http://localhost:8888"}
    client.configure(proxies=proxy)
    assert client.sess.proxies["https"] == proxy["https"]


def test_configure_ssl_verify(client: Client):
    assert client.sess.verify is True
    client.configure(ssl_verify=False)
    assert client.sess.verify is False


def test_configure_timeout(client: Client):
    assert client.timeout == 10
    client.configure(timeout=99)
    assert client.timeout == 99


def test_configure_retry(client: Client):
    assert client.retries == 3
    assert client.sess.adapters["https://"].max_retries.total == client.retries
    client.configure(retries=99)
    assert client.retries == 99
    assert client.sess.adapters["https://"].max_retries.total == 99


def test_configure_status_forcelist(client: Client):
    assert client.status_forcelist == (408, 429, 500, 502, 503, 504)
    assert (
        client.sess.adapters["https://"].max_retries.status_forcelist
        == client.status_forcelist
    )
    client.configure(status_forcelist=(200, 201, 202))
    assert client.status_forcelist == (200, 201, 202)


def test_backoff_factor(client: Client):
    assert client.backoff_factor == 0.5
    assert (
        client.sess.adapters["https://"].max_retries.backoff_factor
        == client.backoff_factor
    )
    client.configure(backoff_factor=0.99)
    assert client.backoff_factor == 0.99
    assert (
        client.sess.adapters["https://"].max_retries.backoff_factor
        == client.backoff_factor
    )


@pytest.mark.vcr
def test_client_request(client: Client):
    resp = client.request("GET", "connect", "/")
    assert resp.ok

    with pytest.raises(GarthHTTPError) as e:
        client.request("GET", "connectapi", "/")
    assert "404" in str(e.value)


@pytest.mark.vcr
def test_login_success_mfa(monkeypatch, client: Client):
    def mock_input(_):
        return "327751"

    monkeypatch.setattr("builtins.input", mock_input)

    assert client.oauth1_token is None
    assert client.oauth2_token is None
    client.login("user@example.com", "correct_password")
    assert client.oauth1_token
    assert client.oauth2_token


@pytest.mark.vcr
def test_username(authed_client: Client):
    assert authed_client._profile is None
    assert authed_client.username
    assert authed_client._profile


@pytest.mark.vcr
def test_connectapi(authed_client: Client):
    stress = authed_client.connectapi(
        "/usersummary-service/stats/stress/daily/2023-07-21/2023-07-21"
    )
    assert stress
    assert isinstance(stress, list)
    assert len(stress) == 1
    assert stress[0]["calendarDate"] == "2023-07-21"
    assert list(stress[0]["values"].keys()) == [
        "highStressDuration",
        "lowStressDuration",
        "overallStressLevel",
        "restStressDuration",
        "mediumStressDuration",
    ]


@pytest.mark.vcr
def test_refresh_oauth2_token(authed_client: Client):
    assert authed_client.oauth2_token
    authed_client.oauth2_token.expires_at = int(time.time())
    assert authed_client.oauth2_token.expired
    profile = authed_client.connectapi("/userprofile-service/socialProfile")
    assert profile
    assert isinstance(profile, dict)
    assert profile["userName"]


@pytest.mark.vcr
def test_download(authed_client: Client):
    downloaded = authed_client.download(
        "/download-service/files/activity/11998957007"
    )
    assert downloaded
    zip_magic_number = b"\x50\x4B\x03\x04"
    assert downloaded[:4] == zip_magic_number
