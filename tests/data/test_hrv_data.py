from datetime import date

import pytest

from garth import HRVData
from garth.http import Client


@pytest.mark.vcr
def test_hrv_data_get(authed_client: Client):
    hrv_data = HRVData.get("2023-07-20", client=authed_client)
    assert hrv_data
    assert hrv_data.user_profile_pk
    assert hrv_data.hrv_summary.calendar_date == date(2023, 7, 20)

    assert HRVData.get("2021-07-20", client=authed_client) is None


@pytest.mark.vcr
def test_hrv_data_list(authed_client: Client):
    days = 2
    end = date(2023, 7, 20)
    hrv_data = HRVData.list(end, days, client=authed_client, max_workers=1)
    assert len(hrv_data) == days
    assert hrv_data[-1].hrv_summary.calendar_date == end
