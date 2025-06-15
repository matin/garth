from datetime import date as date_, datetime, timedelta
from itertools import chain

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import MAX_WORKERS, Data


@dataclass
class WeightData(Data):
    sample_pk: int
    date: int
    calendar_date: date_
    weight: float
    bmi: float | None
    body_fat: float | None
    body_water: float | None
    bone_mass: int | None
    muscle_mass: int | None
    physique_rating: float | None
    visceral_fat: float | None
    metabolic_age: int | None
    source_type: str
    timestamp_gmt: datetime
    weight_delta: float

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

        # Return the most recent weight data for the day
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
        calculated_start = end - timedelta(days=days - 1)

        path = (
            f"/weight-service/weight/range/{calculated_start}/{end}"
            "?includeAll=true"
        )
        data = client.connectapi(path)
        daily_weight_summaries = data["dailyWeightSummaries"] if data else []
        weight_data_list = [
            cls(**camel_to_snake_dict(weight_data))
            for weight_data in chain.from_iterable(
                summary["allWeightMetrics"]
                for summary in daily_weight_summaries
            )
        ]
        return sorted(weight_data_list, key=lambda d: d.calendar_date)
