from datetime import date

import pytest

from garth import DailySleep
from garth.http import Client


@pytest.mark.vcr
def test_daily_sleep(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_sleep = DailySleep.list(end, days, client=authed_client)
    assert daily_sleep[-1].calendar_date == end
    assert len(daily_sleep) == days
