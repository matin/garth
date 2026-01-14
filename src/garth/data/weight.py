from datetime import date, datetime, timedelta, timezone
from itertools import chain

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import (
    camel_to_snake_dict,
    format_end_date,
    get_localized_datetime,
)
from ._base import MAX_WORKERS, Data


@dataclass
class WeightData(Data):
    sample_pk: int
    calendar_date: date
    weight: int
    source_type: str
    weight_delta: float | None
    timestamp_gmt: int
    timestamp_local: int = Field(alias="date")
    bmi: float | None = None
    body_fat: float | None = None
    body_water: float | None = None
    bone_mass: int | None = None
    muscle_mass: int | None = None
    physique_rating: float | None = None
    visceral_fat: float | None = None
    metabolic_age: int | None = None

    @property
    def datetime_utc(self) -> datetime:
        return datetime.fromtimestamp(
            self.timestamp_gmt / 1000, tz=timezone.utc
        )

    @property
    def datetime_local(self) -> datetime:
        return get_localized_datetime(self.timestamp_gmt, self.timestamp_local)

    @classmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> Self | None:
        client = client or http.client
        day = format_end_date(day)
        path = f"/weight-service/weight/dayview/{day}"
        data = client.connectapi(path)
        assert isinstance(data, dict), (
            f"Expected dict from {path}, got {type(data).__name__}"
        )
        day_weight_list = data["dateWeightList"] if data else []

        if not day_weight_list:
            return None

        return cls(**camel_to_snake_dict(day_weight_list[0]))

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        days: int = 1,
        *,
        client: http.Client | None = None,
        max_workers: int = MAX_WORKERS,
    ) -> list[Self]:
        client = client or http.client
        end = format_end_date(end)
        start = end - timedelta(days=days - 1)

        data = client.connectapi(
            f"/weight-service/weight/range/{start}/{end}?includeAll=true"
        )
        assert isinstance(data, dict), (
            f"Expected dict from weight range API, got {type(data).__name__}"
        )
        weight_summaries = data["dailyWeightSummaries"] if data else []
        weight_metrics = chain.from_iterable(
            summary["allWeightMetrics"] for summary in weight_summaries
        )
        weight_data_list = (
            cls(**camel_to_snake_dict(weight_data))
            for weight_data in weight_metrics
        )
        return sorted(weight_data_list, key=lambda d: d.datetime_utc)
