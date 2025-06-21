from datetime import date, timedelta, timezone

import pytest

from garth.data import WeightData
from garth.http import Client


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
