import tempfile
import time

import pytest
from requests import HTTPError
from requests.cookies import RequestsCookieJar

from garth.auth_token import AuthToken
from garth.http import Client


def test_configure_auth_token(client: Client, auth_token: AuthToken):
    assert client.auth_token is None
    client.configure(auth_token=auth_token)
    assert client.auth_token == auth_token


def test_configure_cookies(client: Client):
    cookies = RequestsCookieJar()
    assert client.sess.cookies == {}
    client.configure(cookies=cookies)
    assert client.sess.cookies == cookies


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
    assert client.timeout == 15
    client.configure(timeout=99)
    assert client.timeout == 99


def test_configure_retry(client: Client):
    assert client.retries == 3
    assert client.sess.adapters["https://"].max_retries.total == client.retries
    client.configure(retries=99)
    assert client.retries == 99
    assert client.sess.adapters["https://"].max_retries.total == 99


def test_configure_status_forcelist(client: Client):
    assert client.status_forcelist == (429, 500, 502, 503, 504)
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

    with pytest.raises(HTTPError):
        client.request("GET", "connect", "/", api=True)


@pytest.mark.vcr
def test_login_success(monkeypatch, client: Client):
    def mock_input(_):
        return "327751"

    monkeypatch.setattr("builtins.input", mock_input)

    assert client.auth_token is None
    client.login("user@example.com", "correct_password")
    assert client.auth_token is not None


def test_save_and_resume_session(authed_client: Client):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)

        new_client = Client()
        new_client.load(tempdir)

        assert new_client.sess.cookies == authed_client.sess.cookies
        assert new_client.auth_token == authed_client.auth_token


@pytest.mark.vcr
def test_connectapi(authed_client: Client):
    stress = authed_client.connectapi(
        "/usersummary-service/stats/stress/daily/2023-07-21/2023-07-21"
    )
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
def test_connectapi_refresh(authed_client: Client):
    assert authed_client.auth_token
    authed_client.auth_token.expires_at = int(time.time() - 1)
    assert authed_client.auth_token.expired
    assert not authed_client.auth_token.refresh_expired
    authed_client.connectapi(
        "/usersummary-service/stats/stress/daily/2023-07-21/2023-07-21"
    )
    assert not authed_client.auth_token.expired
