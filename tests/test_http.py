import tempfile
import time
from typing import Any, cast

import pytest
from requests.adapters import HTTPAdapter

from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.exc import GarthHTTPError
from garth.http import Client


def test_dump_and_load(authed_client: Client):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)

        new_client = Client()
        new_client.load(tempdir)

        assert new_client.oauth1_token == authed_client.oauth1_token
        assert new_client.oauth2_token == authed_client.oauth2_token


def test_dumps_and_loads(authed_client: Client):
    s = authed_client.dumps()
    new_client = Client()
    new_client.loads(s)
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
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.total == client.retries

    client.configure(retries=99)
    assert client.retries == 99
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.total == 99


def test_configure_status_forcelist(client: Client):
    assert client.status_forcelist == (408, 429, 500, 502, 503, 504)
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.status_forcelist == client.status_forcelist

    client.configure(status_forcelist=(200, 201, 202))
    assert client.status_forcelist == (200, 201, 202)
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.status_forcelist == client.status_forcelist


def test_configure_backoff_factor(client: Client):
    assert client.backoff_factor == 0.5
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.backoff_factor == client.backoff_factor

    client.configure(backoff_factor=0.99)
    assert client.backoff_factor == 0.99
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.backoff_factor == client.backoff_factor


def test_configure_pool_maxsize(client: Client):
    assert client.pool_maxsize == 10
    client.configure(pool_maxsize=99)
    assert client.pool_maxsize == 99
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.poolmanager.connection_pool_kw["maxsize"] == 99


def test_configure_pool_connections(client: Client):
    client.configure(pool_connections=99)
    assert client.pool_connections == 99
    adapter = client.sess.adapters["https://"]
    assert isinstance(adapter, HTTPAdapter)
    assert getattr(adapter, "_pool_connections", None) == 99, (
        "Pool connections not properly configured"
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
    assert authed_client._user_profile is None
    assert authed_client.username
    assert authed_client._user_profile


@pytest.mark.vcr
def test_profile_alias(authed_client: Client):
    assert authed_client._user_profile is None
    profile = authed_client.profile
    assert profile == authed_client.user_profile
    assert authed_client._user_profile is not None


@pytest.mark.vcr
def test_connectapi(authed_client: Client):
    stress = cast(
        list[dict[str, Any]],
        authed_client.connectapi(
            "/usersummary-service/stats/stress/daily/2023-07-21/2023-07-21"
        ),
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
    assert authed_client.oauth2_token and isinstance(
        authed_client.oauth2_token, OAuth2Token
    )
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
    zip_magic_number = b"\x50\x4b\x03\x04"
    assert downloaded[:4] == zip_magic_number


@pytest.mark.vcr
def test_upload(authed_client: Client):
    fpath = "tests/12129115726_ACTIVITY.fit"
    with open(fpath, "rb") as f:
        uploaded = authed_client.upload(f)
    assert uploaded


@pytest.mark.vcr
def test_delete(authed_client: Client):
    activity_id = "12135235656"
    path = f"/activity-service/activity/{activity_id}"
    assert authed_client.connectapi(path)
    authed_client.delete(
        "connectapi",
        path,
        api=True,
    )
    with pytest.raises(GarthHTTPError) as e:
        authed_client.connectapi(path)
    assert "404" in str(e.value)


@pytest.mark.vcr
def test_put(authed_client: Client):
    data = [
        {
            "changeState": "CHANGED",
            "trainingMethod": "HR_RESERVE",
            "lactateThresholdHeartRateUsed": 170,
            "maxHeartRateUsed": 185,
            "restingHrAutoUpdateUsed": False,
            "sport": "DEFAULT",
            "zone1Floor": 130,
            "zone2Floor": 140,
            "zone3Floor": 150,
            "zone4Floor": 160,
            "zone5Floor": 170,
        }
    ]
    path = "/biometric-service/heartRateZones"
    authed_client.put(
        "connectapi",
        path,
        api=True,
        json=data,
    )
    assert authed_client.connectapi(path)


@pytest.mark.vcr
def test_resume_login(client: Client):
    result = client.login(
        "example@example.com",
        "correct_password",
        return_on_mfa=True,
    )

    assert isinstance(result, tuple)
    result_type, client_state = result

    assert isinstance(client_state, dict)
    assert result_type == "needs_mfa"
    assert "signin_params" in client_state
    assert "client" in client_state

    code = "123456"  # obtain from custom login

    # test resuming the login
    oauth1, oauth2 = client.resume_login(client_state, code)

    assert oauth1
    assert isinstance(oauth1, OAuth1Token)
    assert oauth2
    assert isinstance(oauth2, OAuth2Token)
