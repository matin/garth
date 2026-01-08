from datetime import date

import pytest

from garth import DailySummary
from garth.http import Client


@pytest.mark.vcr
def test_daily_summary_get(authed_client: Client):
    daily_summary = DailySummary.get("2025-06-14", client=authed_client)
    assert daily_summary
    assert daily_summary.user_profile_id
    assert daily_summary.calendar_date == date(2025, 6, 14)


@pytest.mark.vcr
def test_daily_summary_list(authed_client: Client):
    days = 2
    end = date(2025, 6, 14)
    daily_summary = DailySummary.list(
        end, days, client=authed_client, max_workers=1
    )
    assert len(daily_summary) == days
    assert daily_summary[0].calendar_date == end
