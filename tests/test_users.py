import pytest

from garth import UserProfile, UserSettings
from garth.http import Client


@pytest.mark.vcr
def test_user_profile(authed_client: Client):
    profile = UserProfile.get(client=authed_client)
    assert profile.user_name


@pytest.mark.vcr
def test_user_setttings(authed_client: Client):
    settings = UserSettings.get(client=authed_client)
    assert settings.user_data
