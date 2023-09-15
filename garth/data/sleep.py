from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Union

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict, date_range, format_end_date

MAX_WORKERS = 10


@dataclass(frozen=True)
class Score:
    qualifier_key: str
    optimal_start: Optional[float] = None
    optimal_end: Optional[float] = None
    value: Optional[int] = None
    ideal_start_in_seconds: Optional[float] = None
    ideal_end_in_seconds: Optional[float] = None


@dataclass(frozen=True)
class SleepScores:
    total_duration: Score
    stress: Score
    awake_count: Score
    overall: Score
    rem_percentage: Score
    restlessness: Score
    light_percentage: Score
    deep_percentage: Score


@dataclass(frozen=True)
class DailySleepDTO:
    id: int
    user_profile_pk: int
    calendar_date: date
    sleep_time_seconds: int
    nap_time_seconds: int
    sleep_window_confirmed: bool
    sleep_window_confirmation_type: str
    sleep_start_timestamp_gmt: int
    sleep_end_timestamp_gmt: int
    sleep_start_timestamp_local: int
    sleep_end_timestamp_local: int
    unmeasurable_sleep_seconds: int
    deep_sleep_seconds: int
    light_sleep_seconds: int
    rem_sleep_seconds: int
    awake_sleep_seconds: int
    device_rem_capable: bool
    retro: bool
    sleep_from_device: bool
    sleep_version: int
    awake_count: Optional[int] = None
    sleep_scores: Optional[SleepScores] = None
    auto_sleep_start_timestamp_gmt: Optional[int] = None
    auto_sleep_end_timestamp_gmt: Optional[int] = None
    sleep_quality_type_pk: Optional[int] = None
    sleep_result_type_pk: Optional[int] = None
    average_sp_o2_value: Optional[float] = None
    lowest_sp_o2_value: Optional[int] = None
    highest_sp_o2_value: Optional[int] = None
    average_sp_o2_hr_sleep: Optional[float] = None
    average_respiration_value: Optional[float] = None
    lowest_respiration_value: Optional[float] = None
    highest_respiration_value: Optional[float] = None
    avg_sleep_stress: Optional[float] = None
    age_group: Optional[str] = None
    sleep_score_feedback: Optional[str] = None
    sleep_score_insight: Optional[str] = None

    def _get_localized_datetime(
        self, gmt_timestamp: int, local_timestamp: int
    ) -> datetime:
        local_diff = local_timestamp - gmt_timestamp
        local_offset = timezone(timedelta(milliseconds=local_diff))
        gmt_time = datetime.fromtimestamp(gmt_timestamp / 1000, timezone.utc)
        return gmt_time.astimezone(local_offset)

    @property
    def sleep_start(self) -> datetime:
        return self._get_localized_datetime(
            self.sleep_start_timestamp_gmt, self.sleep_start_timestamp_local
        )

    @property
    def sleep_end(self) -> datetime:
        return self._get_localized_datetime(
            self.sleep_end_timestamp_gmt, self.sleep_end_timestamp_local
        )


@dataclass(frozen=True)
class SleepMovement:
    start_gmt: datetime
    end_gmt: datetime
    activity_level: float


@dataclass(frozen=True)
class SleepData:
    daily_sleep_dto: DailySleepDTO
    sleep_movement: List[SleepMovement]

    @classmethod
    def get(
        cls,
        day: Union[date, str],
        *,
        buffer_minutes: int = 60,
        client: Optional[http.Client] = None,
    ) -> Optional["SleepData"]:
        client = client or http.client
        path = (
            f"/wellness-service/wellness/dailySleepData/{client.username}?"
            f"nonSleepBufferMinutes={buffer_minutes}&date={day}"
        )
        sleep_data = client.connectapi(path)
        assert sleep_data
        sleep_data = camel_to_snake_dict(sleep_data)
        assert isinstance(sleep_data, dict)
        return (
            cls(**sleep_data) if sleep_data["daily_sleep_dto"]["id"] else None
        )

    @classmethod
    def list(
        cls,
        end: Union[date, str, None] = None,
        days: int = 1,
        *,
        client: Optional[http.Client] = None,
        max_workers: int = MAX_WORKERS,
    ):
        client = client or http.client
        end = format_end_date(end)
        sleep_data = []

        def fetch_date(date_):
            if day := cls.get(date_, client=client):
                return day

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            dates = date_range(end, days)
            sleep_data = list(executor.map(fetch_date, dates))
            sleep_data = [day for day in sleep_data if day is not None]

        return sorted(
            sleep_data, key=lambda x: x.daily_sleep_dto.calendar_date
        )
