import pytest

from garth import Activity
from garth.http import Client


@pytest.mark.vcr
def test_activity_list(authed_client: Client):
    activities = Activity.list(limit=3, client=authed_client)
    assert len(activities) == 3
    for activity in activities:
        assert activity.activity_id
        assert activity.activity_name
        assert activity.activity_type
        assert activity.activity_type.type_key


@pytest.mark.vcr
def test_activity_get(authed_client: Client):
    # First get an activity ID from the list
    activities = Activity.list(limit=1, client=authed_client)
    assert len(activities) == 1
    activity_id = activities[0].activity_id

    # Now get the full activity details
    activity = Activity.get(activity_id, client=authed_client)
    assert activity.activity_id == activity_id
    assert activity.activity_name
    # Both get and list use activity_type (DTO suffix removed)
    assert activity.activity_type
    assert activity.activity_type.type_key
    assert activity.summary is not None
    assert activity.summary.distance is not None or activity.summary.duration


@pytest.mark.vcr
def test_activity_list_pagination(authed_client: Client):
    # Get first page
    page1 = Activity.list(limit=2, start=0, client=authed_client)
    # Get second page
    page2 = Activity.list(limit=2, start=2, client=authed_client)

    assert len(page1) == 2
    assert len(page2) == 2
    # Ensure different activities
    page1_ids = {a.activity_id for a in page1}
    page2_ids = {a.activity_id for a in page2}
    assert page1_ids.isdisjoint(page2_ids)
