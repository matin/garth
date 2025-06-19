from datetime import date as date_, datetime, timedelta, timezone
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
    calendar_date: date_
    weight: float
    source_type: str
    timestamp_gmt: int
    weight_delta: float
    timestamp: int = Field(..., alias="date")
    bmi: float | None = None
    body_fat: float | None = None
    body_water: float | None = None
    bone_mass: int | None = None
    muscle_mass: int | None = None
    physique_rating: float | None = None
    visceral_fat: float | None = None
    metabolic_age: int | None = None

    @property
    def datetime_local(self) -> datetime:
        return get_localized_datetime(self.timestamp_gmt, self.timestamp)

    @property
    def datetime_utc(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp_gmt / 1000, timezone.utc)

    @classmethod
    def get(
        cls, day: date_ | str, *, client: http.Client | None = None
    ) -> Self | None:
        client = client or http.client
        path = f"/weight-service/weight/dayview/{day}"
        data = client.connectapi(path)
        day_weight_list = data["dateWeightList"] if data else []

        if not day_weight_list:
            return None

        # Get first (most recent) weight entry for the day
        weight_data = camel_to_snake_dict(day_weight_list[0])
        return cls(**weight_data)

    @classmethod
    def list(
        cls,
        end: date_ | str | None = None,
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
        weight_summaries = data["dailyWeightSummaries"] if data else []
        weight_metrics = chain.from_iterable(
            summary["allWeightMetrics"] for summary in weight_summaries
        )
        weight_data_list = (
            cls(**camel_to_snake_dict(weight_data))
            for weight_data in weight_metrics
        )
        return sorted(weight_data_list, key=lambda d: d.timestamp_gmt)
