from datetime import date

import pytest

from garth import DailyIntensityMinutes, WeeklyIntensityMinutes
from garth.http import Client


@pytest.mark.vcr
def test_daily_intensity_minutes(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_im = DailyIntensityMinutes.list(end, days, client=authed_client)
    assert daily_im[-1].calendar_date == end
    assert len(daily_im) == days


@pytest.mark.vcr
def test_weekly_intensity_minutes(authed_client: Client):
    end = date(2023, 7, 20)
    weeks = 12
    weekly_im = WeeklyIntensityMinutes.list(end, weeks, client=authed_client)
    assert len(weekly_im) == weeks
    assert (
        weekly_im[-1].calendar_date.isocalendar()[
            1
        ]  # in python3.9+ [1] can be .week
        == end.isocalendar()[1]
    )
