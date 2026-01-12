from datetime import date

import pytest

from garth import FitnessActivity
from garth.http import Client


@pytest.mark.vcr
def test_fitness_activity_list(authed_client: Client):
    activities = FitnessActivity.list(
        date(2026, 1, 12), days=7, client=authed_client
    )
    assert len(activities) > 0

    # Check that activities are sorted by start_local
    for i in range(len(activities) - 1):
        assert activities[i].start_local <= activities[i + 1].start_local

    # Check that we have required fields
    for activity in activities:
        assert activity.activity_id > 0
        assert activity.start_local is not None
        assert activity.activity_type is not None

    # Check for coaching activities
    coaching = [a for a in activities if a.workout_type == "ADAPTIVE_COACHING"]
    if coaching:
        assert coaching[0].adaptive_coaching_workout_status is not None
