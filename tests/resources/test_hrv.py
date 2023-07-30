from datetime import date

import pytest

from garth import DailyHRV
from garth.http import Client


@pytest.mark.vcr
def test_daily_hrv(authed_client: Client):
    end = date(2023, 7, 20)
    days = 20
    daily_hrv = DailyHRV.list(end, days, client=authed_client)
    assert daily_hrv[-1].calendar_date == end
    assert len(daily_hrv) == days


@pytest.mark.vcr
def test_daily_hrv_paginate(authed_client: Client):
    end = date(2023, 7, 20)
    days = 40
    daily_hrv = DailyHRV.list(end, days, client=authed_client)
    assert daily_hrv[-1].calendar_date == end
    assert len(daily_hrv) == days


@pytest.mark.vcr
def test_daily_hrv_no_results(authed_client: Client):
    end = date(1990, 7, 20)
    daily_hrv = DailyHRV.list(end, client=authed_client)
    assert daily_hrv == []


@pytest.mark.vcr
def test_daily_hrv_paginate_no_results(authed_client: Client):
    end = date(1990, 7, 20)
    days = 40
    daily_hrv = DailyHRV.list(end, days, client=authed_client)
    assert daily_hrv == []
