from datetime import date

import pytest

from garth import DailySummary
from garth.http import Client


@pytest.mark.vcr
def test_daily_summary_get(authed_client: Client):
    daily_summary = DailySummary.get("2023-07-20", client=authed_client)
    assert daily_summary
    assert daily_summary.user_profile_id
    assert daily_summary.calendar_date == date(2023, 7, 20)

    assert DailySummary.get("2021-07-20", client=authed_client) is None


@pytest.mark.vcr
def test_daily_summary_list(authed_client: Client):
    days = 2
    end = date(2023, 7, 20)
    daily_summary = DailySummary.list(
        end, days, client=authed_client, max_workers=1
    )
    assert len(daily_summary) == days
    assert daily_summary[-1].calendar_date == end
