from datetime import date

import pytest

from garth import DailyHydration
from garth.http import Client


@pytest.mark.vcr
def test_daily_hydration(authed_client: Client):
    end = date(2024, 6, 29)
    daily_hydration = DailyHydration.list(end, client=authed_client)
    assert daily_hydration[-1].calendar_date == end
    assert daily_hydration[-1].value_in_ml == 1750.0
    assert daily_hydration[-1].goal_in_ml == 2800.0
