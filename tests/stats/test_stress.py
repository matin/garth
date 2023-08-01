from datetime import date, timedelta

import pytest

from garth import DailyStress, WeeklyStress
from garth.http import Client


@pytest.mark.vcr
def test_daily_stress(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_stress = DailyStress.list(end, days, client=authed_client)
    assert daily_stress[-1].calendar_date == end
    assert len(daily_stress) == days


@pytest.mark.vcr
def test_daily_stress_pagination(authed_client: Client):
    end = date(2023, 7, 20)
    days = 60
    daily_stress = DailyStress.list(end, days, client=authed_client)
    assert len(daily_stress) == days


@pytest.mark.vcr
def test_weekly_stress(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 52
    weekly_stress = WeeklyStress.list(end, weeks, client=authed_client)
    assert len(weekly_stress) == weeks
    assert weekly_stress[-1].calendar_date == end - timedelta(days=6)


@pytest.mark.vcr
def test_weekly_stress_pagination(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 60
    weekly_stress = WeeklyStress.list(end, weeks, client=authed_client)
    assert len(weekly_stress) == weeks
    assert weekly_stress[-1].calendar_date == end - timedelta(days=6)


@pytest.mark.vcr
def test_weekly_stress_beyond_data(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 1000
    weekly_stress = WeeklyStress.list(end, weeks, client=authed_client)
    assert len(weekly_stress) < weeks
