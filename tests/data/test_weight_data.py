from datetime import date, datetime, timedelta, timezone

import pytest

from garth.data import WeightData
from garth.http import Client


def test_weight_data_no_duplicate_alias():
    """Test WeightData instantiation without duplicate parameter errors.

    Verifies that timestamp_gmt (int) and datetime_utc (datetime) don't
    cause Pydantic to raise: ValueError: duplicate parameter name

    See: https://github.com/matin/garth/issues/157
    """
    # Sample data matching API response structure (after camel_to_snake_dict)
    data = {
        "sample_pk": 123456789,
        "calendar_date": date(2025, 1, 15),
        "weight": 70000,
        "source_type": "INDEX_SCALE",
        "weight_delta": 100.0,
        "timestamp_gmt": 1736956800000,  # 2025-01-15 16:00:00 UTC in ms
        "date": 1736935200000,  # Local time in ms
    }

    # This should not raise ValueError: duplicate parameter name
    weight = WeightData(**data)

    # Verify both fields are accessible and correct
    assert weight.timestamp_gmt == 1736956800000
    assert isinstance(weight.datetime_utc, datetime)
    assert weight.datetime_utc.tzinfo == timezone.utc

    # Verify datetime_utc is derived from timestamp_gmt correctly
    expected_utc = datetime.fromtimestamp(
        1736956800000 / 1000, tz=timezone.utc
    )
    assert weight.datetime_utc == expected_utc


def test_weight_data_timestamp_gmt_is_int():
    """Test that timestamp_gmt remains accessible as an integer.

    This ensures that the raw timestamp from the API is preserved,
    not overwritten by the datetime_utc alias.

    See: https://github.com/matin/garth/issues/157
    """
    data = {
        "sample_pk": 123456789,
        "calendar_date": date(2025, 1, 15),
        "weight": 70000,
        "source_type": "INDEX_SCALE",
        "weight_delta": 100.0,
        "timestamp_gmt": 1736956800000,
        "date": 1736935200000,
    }

    weight = WeightData(**data)

    # timestamp_gmt should be an int, not datetime
    assert isinstance(weight.timestamp_gmt, int)
    assert weight.timestamp_gmt == 1736956800000


@pytest.mark.vcr
def test_get_daily_weight_data(authed_client: Client):
    weight_data = WeightData.get(date(2025, 6, 15), client=authed_client)
    assert weight_data is not None
    assert weight_data.source_type == "INDEX_SCALE"
    assert weight_data.weight is not None
    assert weight_data.bmi is not None
    assert weight_data.body_fat is not None
    assert weight_data.body_water is not None
    assert weight_data.bone_mass is not None
    assert weight_data.muscle_mass is not None
    # Timezone should match your account settings, my case is -6
    assert weight_data.datetime_local.tzinfo == timezone(timedelta(hours=-6))
    assert weight_data.datetime_utc.tzinfo == timezone.utc


@pytest.mark.vcr
def test_get_manual_weight_data(authed_client: Client):
    weight_data = WeightData.get(date(2025, 6, 14), client=authed_client)
    assert weight_data is not None
    assert weight_data.source_type == "MANUAL"
    assert weight_data.weight is not None
    assert weight_data.bmi is None
    assert weight_data.body_fat is None
    assert weight_data.body_water is None
    assert weight_data.bone_mass is None
    assert weight_data.muscle_mass is None


@pytest.mark.vcr
def test_get_nonexistent_weight_data(authed_client: Client):
    weight_data = WeightData.get(date(2020, 1, 1), client=authed_client)
    assert weight_data is None


@pytest.mark.vcr
def test_weight_data_list(authed_client: Client):
    end = date(2025, 6, 15)
    days = 15
    weight_data = WeightData.list(end, days, client=authed_client)

    # Only 4 weight entries recorded at time of test
    assert len(weight_data) == 4
    assert all(isinstance(data, WeightData) for data in weight_data)
    assert all(
        weight_data[i].datetime_utc <= weight_data[i + 1].datetime_utc
        for i in range(len(weight_data) - 1)
    )


@pytest.mark.vcr
def test_weight_data_list_single_day(authed_client: Client):
    end = date(2025, 6, 14)
    weight_data = WeightData.list(end, client=authed_client)
    assert len(weight_data) == 2
    assert all(isinstance(data, WeightData) for data in weight_data)
    assert weight_data[0].source_type == "INDEX_SCALE"
    assert weight_data[1].source_type == "MANUAL"


@pytest.mark.vcr
def test_weight_data_list_empty(authed_client: Client):
    end = date(2020, 1, 1)
    days = 15
    weight_data = WeightData.list(end, days, client=authed_client)
    assert len(weight_data) == 0
