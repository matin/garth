import pytest
from requests import HTTPError, Session
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
def test_client_request(session: Session, client: Client):
    resp = client.request("GET", "connect", "/")
    assert resp.ok

    with pytest.raises(HTTPError):
        resp = client.request("GET", "connect", "/", api=True)
