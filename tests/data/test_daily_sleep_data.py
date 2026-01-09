from datetime import date

import pytest

from garth import DailySleepData
from garth.http import Client


@pytest.mark.vcr
def test_daily_sleep_data_get(authed_client: Client):
    data = DailySleepData.get("2025-07-07", client=authed_client)
    assert data is not None
    assert data.daily_sleep_dto.calendar_date == date(2025, 7, 7)
    assert data.daily_sleep_dto.sleep_time_seconds > 0

    # Check sleep need data (coach feature)
    assert data.daily_sleep_dto.sleep_need is not None
    assert data.daily_sleep_dto.sleep_need.baseline > 0
    assert data.daily_sleep_dto.sleep_need.actual > 0
    assert data.sleep_need_minutes is not None

    # Check next sleep need
    assert data.daily_sleep_dto.next_sleep_need is not None
    assert data.next_sleep_need_minutes is not None

    # Check sleep scores
    assert data.daily_sleep_dto.sleep_scores is not None
    assert data.daily_sleep_dto.sleep_scores.overall.value is not None

    # Check additional fields
    assert data.body_battery_change is not None
    assert data.resting_heart_rate is not None

    # Test empty response (far future date)
    data_none = DailySleepData.get("2030-01-01", client=authed_client)
    assert data_none is None


@pytest.mark.vcr
def test_daily_sleep_data_list(authed_client: Client):
    days = 2
    end = date(2025, 7, 7)
    data_list = DailySleepData.list(
        end, days, client=authed_client, max_workers=1
    )
    assert len(data_list) == days
    # Should be sorted by date
    for i in range(len(data_list) - 1):
        assert (
            data_list[i].daily_sleep_dto.calendar_date
            <= data_list[i + 1].daily_sleep_dto.calendar_date
        )
