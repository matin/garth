from datetime import date

import pytest

from garth import SleepData
from garth.http import Client


@pytest.mark.vcr
def test_sleep_data_get(authed_client: Client):
    sleep_data = SleepData.get("2021-07-20", client=authed_client)
    assert sleep_data
    assert sleep_data.daily_sleep_dto.calendar_date == date(2021, 7, 20)
    assert sleep_data.daily_sleep_dto.sleep_start
    assert sleep_data.daily_sleep_dto.sleep_end


@pytest.mark.vcr
def test_sleep_data_list(authed_client: Client):
    end = date(2021, 7, 20)
    days = 20
    sleep_data = SleepData.list(end, days, client=authed_client, max_workers=1)
    assert sleep_data[-1].daily_sleep_dto.calendar_date == end
    assert len(sleep_data) == days
