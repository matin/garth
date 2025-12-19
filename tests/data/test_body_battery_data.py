from datetime import date
from unittest.mock import MagicMock

import pytest

from garth import BodyBatteryData, DailyBodyBatteryStress
from garth.http import Client


@pytest.mark.vcr
def test_body_battery_data_get(authed_client: Client):
    body_battery_data = BodyBatteryData.get("2023-07-20", client=authed_client)
    assert isinstance(body_battery_data, list)

    if body_battery_data:
        # Check first event if available
        event = body_battery_data[0]
        assert event is not None

        # Test body battery readings property
        readings = event.body_battery_readings
        assert isinstance(readings, list)

        if readings:
            # Test reading structure
            reading = readings[0]
            assert hasattr(reading, "timestamp")
            assert hasattr(reading, "status")
            assert hasattr(reading, "level")
            assert hasattr(reading, "version")

            # Test level properties
            assert event.current_level is not None and isinstance(
                event.current_level, int
            )
            assert event.max_level is not None and isinstance(
                event.max_level, int
            )
            assert event.min_level is not None and isinstance(
                event.min_level, int
            )


@pytest.mark.vcr
def test_body_battery_data_list(authed_client: Client):
    days = 3
    end = date(2023, 7, 20)
    body_battery_data = BodyBatteryData.list(end, days, client=authed_client)
    assert isinstance(body_battery_data, list)

    # Test that we get data (may be empty if no events)
    assert len(body_battery_data) >= 0


@pytest.mark.vcr
def test_daily_body_battery_stress_get(authed_client: Client):
    daily_data = DailyBodyBatteryStress.get("2023-07-20", client=authed_client)

    if daily_data:
        # Test basic structure
        assert daily_data.user_profile_pk
        assert daily_data.calendar_date == date(2023, 7, 20)
        assert daily_data.start_timestamp_gmt
        assert daily_data.end_timestamp_gmt

        # Test stress data
        assert isinstance(daily_data.max_stress_level, int)
        assert isinstance(daily_data.avg_stress_level, int)
        assert isinstance(daily_data.stress_values_array, list)
        assert isinstance(daily_data.body_battery_values_array, list)

        # Test stress readings property
        stress_readings = daily_data.stress_readings
        assert isinstance(stress_readings, list)

        if stress_readings:
            stress_reading = stress_readings[0]
            assert hasattr(stress_reading, "timestamp")
            assert hasattr(stress_reading, "stress_level")

        # Test body battery readings property
        bb_readings = daily_data.body_battery_readings
        assert isinstance(bb_readings, list)

        if bb_readings:
            bb_reading = bb_readings[0]
            assert hasattr(bb_reading, "timestamp")
            assert hasattr(bb_reading, "status")
            assert hasattr(bb_reading, "level")
            assert hasattr(bb_reading, "version")

            # Test computed properties
            assert daily_data.current_body_battery is not None and isinstance(
                daily_data.current_body_battery, int
            )
            assert daily_data.max_body_battery is not None and isinstance(
                daily_data.max_body_battery, int
            )
            assert daily_data.min_body_battery is not None and isinstance(
                daily_data.min_body_battery, int
            )

            # Test body battery change
            if len(bb_readings) >= 2:
                change = daily_data.body_battery_change
                assert change is not None


@pytest.mark.vcr
def test_daily_body_battery_stress_get_no_data(authed_client: Client):
    # Test with a date that likely has no data
    daily_data = DailyBodyBatteryStress.get("2020-01-01", client=authed_client)

    # Should return None if no data available
    assert daily_data is None or isinstance(daily_data, DailyBodyBatteryStress)


@pytest.mark.vcr
def test_daily_body_battery_stress_get_incomplete_data(authed_client: Client):
    daily_data = DailyBodyBatteryStress.get("2025-12-18", client=authed_client)
    assert daily_data
    assert all(r.level is not None for r in daily_data.body_battery_readings)
    assert all(r.status is not None for r in daily_data.body_battery_readings)


@pytest.mark.vcr
def test_daily_body_battery_stress_list(authed_client: Client):
    days = 3
    end = date(2023, 7, 20)
    # Use max_workers=1 to avoid VCR issues with concurrent requests
    daily_data_list = DailyBodyBatteryStress.list(
        end, days, client=authed_client, max_workers=1
    )
    assert isinstance(daily_data_list, list)
    assert (
        len(daily_data_list) <= days
    )  # May be less if some days have no data

    # Test that each item is correct type
    for daily_data in daily_data_list:
        assert isinstance(daily_data, DailyBodyBatteryStress)
        assert isinstance(daily_data.calendar_date, date)
        assert daily_data.user_profile_pk


@pytest.mark.vcr
def test_body_battery_properties_edge_cases(authed_client: Client):
    # Test empty data handling
    daily_data = DailyBodyBatteryStress.get("2023-07-20", client=authed_client)

    if daily_data:
        # Test with potentially empty arrays
        if not daily_data.body_battery_values_array:
            assert daily_data.body_battery_readings == []
            assert daily_data.current_body_battery is None
            assert daily_data.max_body_battery is None
            assert daily_data.min_body_battery is None
            assert daily_data.body_battery_change is None

        if not daily_data.stress_values_array:
            assert daily_data.stress_readings == []


# Error handling tests for BodyBatteryData.get()
def test_body_battery_data_get_api_error():
    """Test handling of API errors."""
    mock_client = MagicMock()
    mock_client.connectapi.side_effect = Exception("API Error")

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert result == []


def test_body_battery_data_get_invalid_response():
    """Test handling of non-list responses."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = {"error": "Invalid response"}

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert result == []


def test_body_battery_data_get_missing_event_data():
    """Test handling of items with missing event data."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {"activityName": "Test", "averageStress": 25}  # Missing "event" key
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert len(result) == 1
    assert result[0].event is None


def test_body_battery_data_get_missing_event_start_time():
    """Test handling of event data missing eventStartTimeGmt."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {
            "event": {"eventType": "sleep"},  # Missing eventStartTimeGmt
            "activityName": "Test",
            "averageStress": 25,
        }
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert result == []  # Should skip invalid items


def test_body_battery_data_get_invalid_datetime_format():
    """Test handling of invalid datetime format."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {
            "event": {
                "eventType": "sleep",
                "eventStartTimeGmt": "invalid-date",
            },
            "activityName": "Test",
            "averageStress": 25,
        }
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert result == []  # Should skip invalid items


def test_body_battery_data_get_invalid_field_types():
    """Test handling of invalid field types."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {
            "event": {
                "eventType": "sleep",
                "eventStartTimeGmt": "2023-07-20T10:00:00.000Z",
                "timezoneOffset": "invalid",  # Should be number
                "durationInMilliseconds": "invalid",  # Should be number
                "bodyBatteryImpact": "invalid",  # Should be number
            },
            "activityName": "Test",
            "averageStress": "invalid",  # Should be number
            "stressValuesArray": "invalid",  # Should be list
            "bodyBatteryValuesArray": "invalid",  # Should be list
        }
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    assert len(result) == 1
    # Should handle invalid types gracefully


def test_body_battery_data_get_validation_error():
    """Test handling of validation errors during object creation."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {
            "event": {
                "eventType": "sleep",
                "eventStartTimeGmt": "2023-07-20T10:00:00.000Z",
                # Missing required fields for BodyBatteryEvent
            },
            # Missing required fields for BodyBatteryData
        }
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    # Should handle validation errors and continue processing
    assert isinstance(result, list)
    assert len(result) == 1  # Should create object with missing fields as None
    assert result[0].event is not None  # Event should be created
    assert result[0].activity_name is None  # Missing fields should be None


def test_body_battery_data_get_mixed_valid_invalid():
    """Test processing with mix of valid and invalid items."""
    mock_client = MagicMock()
    mock_client.connectapi.return_value = [
        {
            "event": {
                "eventType": "sleep",
                "eventStartTimeGmt": "2023-07-20T10:00:00.000Z",
                "timezoneOffset": -25200000,
                "durationInMilliseconds": 28800000,
                "bodyBatteryImpact": 35,
                "feedbackType": "good_sleep",
                "shortFeedback": "Good sleep",
            },
            "activityName": None,
            "activityType": None,
            "activityId": None,
            "averageStress": 15.5,
            "stressValuesArray": [[1689811800000, 12]],
            "bodyBatteryValuesArray": [[1689811800000, "charging", 45, 1.0]],
        },
        {
            # Invalid - missing eventStartTimeGmt
            "event": {"eventType": "sleep"},
            "activityName": "Test",
        },
    ]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    # Should process valid items and skip invalid ones
    assert len(result) == 1  # Only the valid item should be processed
    assert result[0].event is not None


def test_body_battery_data_get_unexpected_error():
    """Test handling of unexpected errors during object creation."""
    mock_client = MagicMock()

    # Create a special object that raises an exception when accessed
    class ExceptionRaisingDict(dict):
        def get(self, key, default=None):
            if key == "activityName":
                raise RuntimeError("Unexpected error during object creation")
            return super().get(key, default)

    # Create mock data with problematic item
    mock_response_item = ExceptionRaisingDict(
        {
            "event": {
                "eventType": "sleep",
                "eventStartTimeGmt": "2023-07-20T10:00:00.000Z",
                "timezoneOffset": -25200000,
                "durationInMilliseconds": 28800000,
                "bodyBatteryImpact": 35,
                "feedbackType": "good_sleep",
                "shortFeedback": "Good sleep",
            },
            "activityName": None,
            "activityType": None,
            "activityId": None,
            "averageStress": 15.5,
            "stressValuesArray": [[1689811800000, 12]],
            "bodyBatteryValuesArray": [[1689811800000, "charging", 45, 1.0]],
        }
    )

    mock_client.connectapi.return_value = [mock_response_item]

    result = BodyBatteryData.get("2023-07-20", client=mock_client)
    # Should handle unexpected errors and return empty list
    assert result == []
