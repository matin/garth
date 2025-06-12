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
    # Verify datetime types
    if daily_training_status[0].since_date is not None:
        assert isinstance(daily_training_status[0].since_date, date)
    if daily_training_status[0].timestamp is not None:
        from datetime import datetime

        assert isinstance(daily_training_status[0].timestamp, datetime)


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
    assert monthly_training_status == []


def test_training_status_extract_data_error_cases():
    """Test error handling in _parse_response methods."""
    from garth.stats.training_status import (
        DailyTrainingStatus,
        MonthlyTrainingStatus,
        WeeklyTrainingStatus,
    )

    # Test daily endpoint error cases
    result = DailyTrainingStatus._parse_response({})
    assert result == []

    result = DailyTrainingStatus._parse_response(
        {"mostRecentTrainingStatus": "not a dict"}
    )
    assert result == []

    result = DailyTrainingStatus._parse_response(
        {"mostRecentTrainingStatus": {"payload": "not a dict"}}
    )
    assert result == []

    result = DailyTrainingStatus._parse_response(
        {
            "mostRecentTrainingStatus": {
                "payload": {"latestTrainingStatusData": "not a dict"}
            }
        }
    )
    assert result == []

    # Test weekly endpoint error cases
    result = WeeklyTrainingStatus._parse_response({})
    assert result == []

    result = WeeklyTrainingStatus._parse_response(
        {"weeklyTrainingStatus": "not a dict"}
    )
    assert result == []

    result = WeeklyTrainingStatus._parse_response(
        {"weeklyTrainingStatus": {"payload": "not a dict"}}
    )
    assert result == []

    result = WeeklyTrainingStatus._parse_response(
        {"weeklyTrainingStatus": {"payload": {"reportData": "not a dict"}}}
    )
    assert result == []

    # Test monthly endpoint error cases
    result = MonthlyTrainingStatus._parse_response({})
    assert result == []

    result = MonthlyTrainingStatus._parse_response(
        {"monthlyTrainingStatus": "not a dict"}
    )
    assert result == []

    result = MonthlyTrainingStatus._parse_response(
        {"monthlyTrainingStatus": {"payload": "not a dict"}}
    )
    assert result == []

    result = MonthlyTrainingStatus._parse_response(
        {"monthlyTrainingStatus": {"payload": {"reportData": "not a dict"}}}
    )
    assert result == []


def test_training_status_list_error_cases():
    """Test error handling in list method."""
    from unittest.mock import Mock

    from garth.stats.training_status import (
        DailyTrainingStatus,
        MonthlyTrainingStatus,
        WeeklyTrainingStatus,
    )

    # Test with non-dict response from connectapi
    mock_client = Mock()
    mock_client.connectapi.return_value = "not a dict"

    result = DailyTrainingStatus.list(date(2025, 6, 11), 1, client=mock_client)
    assert result == []

    result = WeeklyTrainingStatus.list(
        date(2025, 6, 11), 1, client=mock_client
    )
    assert result == []

    result = MonthlyTrainingStatus.list(
        date(2025, 6, 11), 1, client=mock_client
    )
    assert result == []

    # Test with empty response
    mock_client.connectapi.return_value = {}
    result = DailyTrainingStatus.list(date(2025, 6, 11), 1, client=mock_client)
    assert result == []

    result = WeeklyTrainingStatus.list(
        date(2025, 6, 11), 1, client=mock_client
    )
    assert result == []

    result = MonthlyTrainingStatus.list(
        date(2025, 6, 11), 1, client=mock_client
    )
    assert result == []


def test_daily_training_status_period_type():
    """Test that daily training status uses correct period type (days)."""
    from unittest.mock import Mock, patch

    from garth.stats.training_status import DailyTrainingStatus

    mock_client = Mock()
    mock_client.connectapi.return_value = {
        "mostRecentTrainingStatus": {
            "payload": {
                "latestTrainingStatusData": {
                    "device1": {
                        "calendarDate": "2025-06-09",
                        "trainingStatus": 1,
                    }
                }
            }
        }
    }

    # Test that period type is correctly set to "days"
    # Note: Daily training status only uses {end} in path, so it calls the same
    # "latest" endpoint regardless of period, but the _period_type ensures
    # date calculations use days instead of weeks
    assert DailyTrainingStatus._period_type == "days"

    # Test single day request works
    with patch("garth.stats._base.format_end_date") as mock_format:
        mock_format.return_value = date(2025, 6, 11)

        result = DailyTrainingStatus.list(
            date(2025, 6, 11), 1, client=mock_client
        )

        # Should call the latest endpoint with the end date
        expected_path = (
            "/mobile-gateway/usersummary/trainingstatus/latest/2025-06-11"
        )
        mock_client.connectapi.assert_called_with(expected_path)
        assert len(result) == 1


def test_training_status_pagination_edge_cases():
    """Test pagination edge cases."""
    from unittest.mock import Mock

    from garth.stats.training_status import (
        MonthlyTrainingStatus,
        WeeklyTrainingStatus,
    )

    # Test monthly pagination when first page is empty
    mock_client = Mock()
    mock_client.connectapi.return_value = {}

    result = MonthlyTrainingStatus.list(
        date(2025, 6, 11), 15, client=mock_client
    )
    assert result == []

    # Test weekly pagination when first page is empty
    result = WeeklyTrainingStatus.list(
        date(2025, 6, 11), 60, client=mock_client
    )
    assert result == []

    # Test monthly pagination with data to trigger remaining_page call
    mock_response = {
        "monthlyTrainingStatus": {
            "payload": {
                "reportData": {
                    "device1": [
                        {
                            "calendarDate": "2025-01-01",
                            "sinceDate": "2025-01-01",
                            "trainingStatus": 1,
                            "acuteTrainingLoadDTO": {
                                "dailyTrainingLoadAcute": 50
                            },
                        }
                    ]
                }
            }
        }
    }

    def mock_connectapi_side_effect(path):
        # First call returns data, subsequent calls return empty
        if hasattr(mock_connectapi_side_effect, "call_count"):
            mock_connectapi_side_effect.call_count += 1
            return {}
        mock_connectapi_side_effect.call_count = 1
        return mock_response

    mock_client.connectapi.side_effect = mock_connectapi_side_effect

    # Test with period > page_size to trigger pagination logic
    result = MonthlyTrainingStatus.list(
        date(2025, 6, 11), 15, client=mock_client
    )
    assert len(result) == 1
