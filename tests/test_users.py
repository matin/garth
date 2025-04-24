import pytest

from garth import UserProfile, UserSettings
from garth.http import Client


@pytest.mark.vcr
def test_user_profile(authed_client: Client):
    profile = UserProfile.get(client=authed_client)
    assert profile.user_name


@pytest.mark.vcr
def test_user_settings(authed_client: Client):
    settings = UserSettings.get(client=authed_client)
    assert settings.user_data


@pytest.mark.vcr
def test_user_settings_sleep_windows(authed_client: Client):
    settings = UserSettings.get(client=authed_client)
    assert settings.user_data
    assert isinstance(settings.user_sleep_windows, list)
    for window in settings.user_sleep_windows:
        assert hasattr(window, "sleep_window_frequency")
        assert hasattr(window, "start_sleep_time_seconds_from_midnight")
        assert hasattr(window, "end_sleep_time_seconds_from_midnight")
