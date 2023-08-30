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
