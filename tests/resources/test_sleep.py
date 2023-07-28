from datetime import date

import pytest

from garth import DailySleep, SleepData
from garth.http import Client


@pytest.mark.vcr
def test_daily_sleep(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_sleep = DailySleep.list(end, days, client=authed_client)
    assert daily_sleep[-1].calendar_date == end
    assert len(daily_sleep) == days


@pytest.mark.vcr
def test_sleep_data_get(authed_client: Client):
    sleep_data = SleepData.get("2021-07-20", client=authed_client)
    assert sleep_data.daily_sleep_dto.calendar_date == date(2021, 7, 20)


@pytest.mark.vcr
def test_sleep_data_list(authed_client: Client):
    end = date(2021, 7, 20)
    days = 20
    sleep_data = SleepData.list(end, days, client=authed_client)
    assert sleep_data[-1].daily_sleep_dto.calendar_date == end
    assert len(sleep_data) == days
