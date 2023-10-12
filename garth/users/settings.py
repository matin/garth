from datetime import date
from typing import Dict, List, Optional

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict


@dataclass
class PowerFormat:
    format_id: int
    format_key: str
    min_fraction: int
    max_fraction: int
    grouping_used: bool
    display_format: Optional[str]


@dataclass
class FirstDayOfWeek:
    day_id: int
    day_name: str
    sort_order: int
    is_possible_first_day: bool


@dataclass
class WeatherLocation:
    use_fixed_location: bool
    latitude: float
    longitude: float
    location_name: str
    iso_country_code: str
    postal_code: str


@dataclass
class UserData:
    gender: str
    weight: float
    height: float
    time_format: str
    birth_date: date
    measurement_system: str
    activity_level: Optional[str]
    handedness: str
    power_format: PowerFormat
    heart_rate_format: PowerFormat
    first_day_of_week: FirstDayOfWeek
    vo_2_max_running: Optional[float]
    vo_2_max_cycling: Optional[float]
    lactate_threshold_speed: Optional[float]
    lactate_threshold_heart_rate: Optional[float]
    dive_number: Optional[int]
    intensity_minutes_calc_method: str
    moderate_intensity_minutes_hr_zone: int
    vigorous_intensity_minutes_hr_zone: int
    hydration_measurement_unit: str
    hydration_containers: List[Dict[str, Optional[float]]]
    hydration_auto_goal_enabled: bool
    firstbeat_max_stress_score: Optional[float]
    firstbeat_cycling_lt_timestamp: Optional[int]
    firstbeat_running_lt_timestamp: Optional[int]
    threshold_heart_rate_auto_detected: bool
    ftp_auto_detected: Optional[bool]
    training_status_paused_date: Optional[str]
    weather_location: Optional[WeatherLocation]
    golf_distance_unit: str
    golf_elevation_unit: Optional[str]
    golf_speed_unit: Optional[str]
    external_bottom_time: Optional[float]


@dataclass
class UserSleep:
    sleep_time: int
    default_sleep_time: bool
    wake_time: int
    default_wake_time: bool


@dataclass
class UserSettings:
    id: int
    user_data: UserData
    user_sleep: UserSleep
    connect_date: Optional[str]
    source_type: Optional[str]

    @classmethod
    def get(cls, /, client: Optional[http.Client] = None):
        client = client or http.client
        settings = client.connectapi(
            "/userprofile-service/userprofile/user-settings"
        )
        assert isinstance(settings, dict)
        return cls(**camel_to_snake_dict(settings))
