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


def test_activity_update_validation():
    with pytest.raises(ValueError, match="At least one of"):
        Activity.update(123)


@pytest.mark.vcr
def test_activity_update(authed_client: Client):
    activity_id = 21522899847

    # Get original name
    original = Activity.get(activity_id, client=authed_client)
    original_name = original.activity_name

    # Update to new name
    Activity.update(activity_id, name="Test Rename", client=authed_client)

    # Verify change
    updated = Activity.get(activity_id, client=authed_client)
    assert updated.activity_name == "Test Rename"

    # Revert to original name
    Activity.update(activity_id, name=original_name, client=authed_client)
