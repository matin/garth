import pytest

from garth import UserProfile
from garth.http import Client


@pytest.mark.vcr
def test_user_profile(authed_client: Client):
    profile = UserProfile.get(client=authed_client)
    assert profile.user_name
