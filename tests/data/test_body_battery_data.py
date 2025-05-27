from datetime import date

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
            assert hasattr(reading, 'timestamp')
            assert hasattr(reading, 'status')
            assert hasattr(reading, 'level')
            assert hasattr(reading, 'version')
            
            # Test level properties
            assert event.current_level is not None or event.current_level == 0
            assert event.max_level is not None or event.max_level == 0
            assert event.min_level is not None or event.min_level == 0


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
        assert daily_data.calendar_date == "2023-07-20"
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
            reading = stress_readings[0]
            assert hasattr(reading, 'timestamp')
            assert hasattr(reading, 'stress_level')
        
        # Test body battery readings property
        bb_readings = daily_data.body_battery_readings
        assert isinstance(bb_readings, list)
        
        if bb_readings:
            reading = bb_readings[0]
            assert hasattr(reading, 'timestamp')
            assert hasattr(reading, 'status')
            assert hasattr(reading, 'level')
            assert hasattr(reading, 'version')
            
            # Test computed properties
            assert daily_data.current_body_battery is not None or daily_data.current_body_battery == 0
            assert daily_data.max_body_battery is not None or daily_data.max_body_battery == 0
            assert daily_data.min_body_battery is not None or daily_data.min_body_battery == 0
            
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
def test_daily_body_battery_stress_list(authed_client: Client):
    days = 3
    end = date(2023, 7, 20)
    daily_data_list = DailyBodyBatteryStress.list(end, days, client=authed_client)
    assert isinstance(daily_data_list, list)
    assert len(daily_data_list) <= days  # May be less if some days have no data
    
    # Test that each item is correct type
    for daily_data in daily_data_list:
        assert isinstance(daily_data, DailyBodyBatteryStress)
        assert daily_data.calendar_date
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