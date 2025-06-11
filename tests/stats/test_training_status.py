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


def test_training_status_extract_data_error_cases():
    """Test error handling in _extract_training_data method."""
    from garth.stats.training_status import DailyTrainingStatus

    # Test with non-dict response
    result = DailyTrainingStatus._extract_training_data("not a dict", "key")
    assert result == []

    # Test with missing data section
    result = DailyTrainingStatus._extract_training_data({}, "missingKey")
    assert result == []

    # Test with non-dict data section
    result = DailyTrainingStatus._extract_training_data(
        {"key": "not a dict"}, "key"
    )
    assert result == []

    # Test with missing payload
    result = DailyTrainingStatus._extract_training_data(
        {"mostRecentTrainingStatus": {}}, "mostRecentTrainingStatus"
    )
    assert result == []

    # Test with non-dict payload
    result = DailyTrainingStatus._extract_training_data(
        {"mostRecentTrainingStatus": {"payload": "not a dict"}},
        "mostRecentTrainingStatus",
    )
    assert result == []

    # Test daily endpoint with missing latestTrainingStatusData
    result = DailyTrainingStatus._extract_training_data(
        {"mostRecentTrainingStatus": {"payload": {}}},
        "mostRecentTrainingStatus",
    )
    assert result == []

    # Test daily endpoint with non-dict latestTrainingStatusData
    result = DailyTrainingStatus._extract_training_data(
        {
            "mostRecentTrainingStatus": {
                "payload": {"latestTrainingStatusData": "not a dict"}
            }
        },
        "mostRecentTrainingStatus",
    )
    assert result == []

    # Test weekly/monthly endpoint with missing reportData
    result = DailyTrainingStatus._extract_training_data(
        {"weeklyTrainingStatus": {"payload": {}}}, "weeklyTrainingStatus"
    )
    assert result == []

    # Test weekly/monthly endpoint with non-dict reportData
    result = DailyTrainingStatus._extract_training_data(
        {"weeklyTrainingStatus": {"payload": {"reportData": "not a dict"}}},
        "weeklyTrainingStatus",
    )
    assert result == []


def test_training_status_list_error_cases():
    """Test error handling in list method."""
    from unittest.mock import Mock

    from garth.stats.training_status import DailyTrainingStatus

    # Test with non-dict response from connectapi
    mock_client = Mock()
    mock_client.connectapi.return_value = "not a dict"

    result = DailyTrainingStatus.list(date(2025, 6, 11), 1, client=mock_client)
    assert result == []

    # Test pagination when first page is empty
    mock_client.connectapi.return_value = {}
    result = DailyTrainingStatus.list(
        date(2025, 6, 11), 50, client=mock_client
    )
    assert result == []
