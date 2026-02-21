import pytest

from garth import Badge
from garth.http import Client

@pytest.mark.vcr
def test_badge_list(authed_client: Client):
    badges = Badge.list(client=authed_client)
    assert len(badges) == 6
    assert len([b for b in badges if b.earned_by_me]) == 3
    for badge in badges:
        assert badge.badge_id
        assert badge.badge_name
        assert badge.badge_category_id
        assert badge.badge_type_ids
        assert badge.badge_assoc_type_id

    badge = next(b for b in badges if b.badge_id == 1136)
    
    assert badge.badge_target_value == 30
    assert badge.badge_progress_value == 30 # in list it's always equal target for earned

@pytest.mark.vcr
def test_badge_get(authed_client: Client):
    badge = Badge.get(1136, client=authed_client)
    assert badge.badge_id

    assert badge.badge_target_value == 30
    assert badge.badge_progress_value == 5

