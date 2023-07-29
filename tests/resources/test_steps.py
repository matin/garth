from datetime import date, timedelta

import pytest

from garth import DailySteps, WeeklySteps
from garth.http import Client


@pytest.mark.vcr
def test_daily_steps(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_steps = DailySteps.list(end, days, client=authed_client)
    assert daily_steps[-1].calendar_date == end
    assert len(daily_steps) == days


@pytest.mark.vcr
def test_weekly_steps(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 52
    weekly_steps = WeeklySteps.list(end, weeks, client=authed_client)
    assert len(weekly_steps) == weeks
    assert weekly_steps[-1].calendar_date == end - timedelta(days=6)
