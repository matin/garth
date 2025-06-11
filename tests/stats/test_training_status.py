from datetime import date

import pytest

from garth import (
    DailyTrainingStatus,
    MonthlyTrainingStatus,
    WeeklyTrainingStatus,
)
from garth.http import Client


@pytest.mark.vcr
def test_daily_training_status(authed_client: Client):
    end = date(2025, 6, 11)
    daily_training_status = DailyTrainingStatus.list(
        end, 1, client=authed_client
    )
    assert len(daily_training_status) == 1
    assert daily_training_status[0].calendar_date == end
    assert daily_training_status[0].training_status is not None


@pytest.mark.vcr
def test_weekly_training_status(authed_client: Client):
    end = date(2025, 6, 11)
    weeks = 4  # Use a smaller, more reasonable period
    weekly_training_status = WeeklyTrainingStatus.list(
        end, weeks, client=authed_client
    )
    assert len(weekly_training_status) > 0
    assert all(ts.training_status is not None for ts in weekly_training_status)


@pytest.mark.vcr
def test_monthly_training_status(authed_client: Client):
    end = date(2025, 6, 11)
    months = 6  # Use a smaller, more reasonable period
    monthly_training_status = MonthlyTrainingStatus.list(
        end, months, client=authed_client
    )
    assert len(monthly_training_status) > 0
    assert all(
        ts.training_status is not None for ts in monthly_training_status
    )


@pytest.mark.vcr
def test_weekly_training_status_pagination(authed_client: Client):
    end = date(2025, 6, 11)
    weeks = 60
    weekly_training_status = WeeklyTrainingStatus.list(
        end, weeks, client=authed_client
    )
    assert len(weekly_training_status) > 0


@pytest.mark.vcr
def test_monthly_training_status_no_data(authed_client: Client):
    end = date(2020, 1, 1)  # Date far in the past with no data
    monthly_training_status = MonthlyTrainingStatus.list(
        end, 1, client=authed_client
    )
    # Should return empty list if no data
    assert isinstance(monthly_training_status, list)
