from datetime import date, datetime

import pytest
from freezegun import freeze_time

from garth import DailyHydration
from garth.http import Client
from garth.stats.hydration import HydrationLogEntry


@pytest.mark.vcr
def test_daily_hydration(authed_client: Client):
    end = date(2024, 6, 29)
    daily_hydration = DailyHydration.list(end, client=authed_client)
    assert daily_hydration[-1].calendar_date == end
    assert daily_hydration[-1].value_in_ml == 1750.0
    assert daily_hydration[-1].goal_in_ml == 2800.0


@pytest.mark.vcr
def test_daily_hydration_log(authed_client: Client):
    timestamp = datetime(2026, 1, 9, 15, 30, 0)
    entry = DailyHydration.log(
        500.0, timestamp=timestamp, client=authed_client
    )
    assert isinstance(entry, HydrationLogEntry)
    assert entry.calendar_date == date(2026, 1, 9)
    assert entry.value_in_ml == 1000.0  # 500 existing + 500 logged
    assert entry.last_entry_timestamp_local == timestamp


@pytest.mark.vcr
@freeze_time("2026-01-09 15:30:00")
def test_daily_hydration_log_default_timestamp(authed_client: Client):
    entry = DailyHydration.log(500.0, client=authed_client)
    assert isinstance(entry, HydrationLogEntry)
    assert entry.calendar_date == date(2026, 1, 9)
    assert entry.last_entry_timestamp_local == datetime(2026, 1, 9, 15, 30, 0)
