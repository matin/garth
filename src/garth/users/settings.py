from datetime import date

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict


@dataclass
class PowerFormat:
    format_id: int
    format_key: str
    min_fraction: int
    max_fraction: int
    grouping_used: bool
    display_format: str | None


@dataclass
class FirstDayOfWeek:
    day_id: int
    day_name: str
    sort_order: int
    is_possible_first_day: bool


@dataclass
class WeatherLocation:
    use_fixed_location: bool | None
    latitude: float | None
    longitude: float | None
    location_name: str | None
    iso_country_code: str | None
    postal_code: str | None


@dataclass
class UserData:
    gender: str
    weight: float
    height: float
    time_format: str
    birth_date: date
    measurement_system: str
    activity_level: int | None
    handedness: str
    power_format: PowerFormat
    heart_rate_format: PowerFormat
    first_day_of_week: FirstDayOfWeek
    vo_2_max_running: float | None
    vo_2_max_cycling: float | None
    lactate_threshold_speed: float | None
    lactate_threshold_heart_rate: float | None
    dive_number: int | None
    intensity_minutes_calc_method: str
    moderate_intensity_minutes_hr_zone: int
    vigorous_intensity_minutes_hr_zone: int
    hydration_measurement_unit: str
    hydration_containers: list[dict[str, float | str | None]]
    hydration_auto_goal_enabled: bool
    firstbeat_max_stress_score: float | None
    firstbeat_cycling_lt_timestamp: int | None
    firstbeat_running_lt_timestamp: int | None
    threshold_heart_rate_auto_detected: bool
    ftp_auto_detected: bool | None
    training_status_paused_date: str | None
    weather_location: WeatherLocation | None
    golf_distance_unit: str | None
    golf_elevation_unit: str | None
    golf_speed_unit: str | None
    external_bottom_time: float | None


@dataclass
class UserSleep:
    sleep_time: int
    default_sleep_time: bool
    wake_time: int
    default_wake_time: bool


@dataclass
class UserSleepWindow:
    sleep_window_frequency: str
    start_sleep_time_seconds_from_midnight: int
    end_sleep_time_seconds_from_midnight: int


@dataclass
class UserSettings:
    id: int
    user_data: UserData
    user_sleep: UserSleep
    connect_date: str | None
    source_type: str | None
    user_sleep_windows: list[UserSleepWindow] | None = None

    @classmethod
    def get(cls, /, client: http.Client | None = None) -> Self:
        client = client or http.client
        settings = client.connectapi(
            "/userprofile-service/userprofile/user-settings"
        )
        assert isinstance(settings, dict)
        data = camel_to_snake_dict(settings)
        return cls(**data)
