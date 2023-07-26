from datetime import date, timedelta

import pytest

from garth import DailyStress, WeeklyStress
from garth.http import Client


@pytest.mark.vcr
def test_daily(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_stress = DailyStress.get(end, days, client=authed_client)
    assert daily_stress[-1].calendar_date == end
    assert len(daily_stress) == days


@pytest.mark.vcr
def test_daily_pagination(authed_client: Client):
    end = date(2023, 7, 20)
    days = 30
    daily_stress = DailyStress.get(end, days, client=authed_client)
    assert len(daily_stress) == days


@pytest.mark.vcr
def test_weekly(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 52
    weekly_stress = WeeklyStress.get(end, weeks, client=authed_client)
    assert len(weekly_stress) == weeks
    assert weekly_stress[-1].calendar_date == end - timedelta(days=6)


@pytest.mark.vcr
def test_weekly_pagination(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 60
    weekly_stress = WeeklyStress.get(end, weeks, client=authed_client)
    assert len(weekly_stress) == weeks
    assert weekly_stress[-1].calendar_date == end - timedelta(days=6)
