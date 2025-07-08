from datetime import date

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import (
    camel_to_snake_dict,
)
from ._base import Data


@dataclass
class GarminScoresData(Data):
    user_profile_pk: int
    calendar_date: date
    endurance_score: int
    endurance_classification: int
    endurance_classification_lower_limit_elite: int
    endurance_classification_lower_limit_superior: int
    endurance_classification_lower_limit_expert: int
    endurance_classification_lower_limit_well_trained: int
    endurance_classification_lower_limit_trained: int
    endurance_classification_lower_limit_intermediate: int
    hill_score: int
    hill_endurance_score: int
    hill_strength_score: int
    vo_2_max: float
    vo_2_max_precise_value: float

    @classmethod
    def get(
        cls, day: date | str, *, client: http.Client | None = None
    ) -> Self | None:
        client = client or http.client
        path_hill_score = "/metrics-service/metrics/hillscore"
        path_endurance_score = "/metrics-service/metrics/endurancescore"
        data_hill_score = client.connectapi(
            path_hill_score, params={"calendarDate": day}
        )
        data_endurance_score = client.connectapi(
            path_endurance_score, params={"calendarDate": day}
        )

        if not data_hill_score or not data_endurance_score:
            return None

        data_hill_score = camel_to_snake_dict(data_hill_score)
        data_endurance_score = camel_to_snake_dict(data_endurance_score)
        data_hill_score["hill_score"] = data_hill_score.pop("overall_score")
        data_hill_score["hill_endurance_score"] = data_hill_score.pop(
            "endurance_score"
        )
        data_hill_score["hill_strength_score"] = data_hill_score.pop(
            "strength_score"
        )
        data_endurance_score["endurance_score"] = data_endurance_score.pop(
            "overall_score"
        )
        data_endurance_score = {
            ("endurance_classification" + key[len("classification") :])
            if key.startswith("classification")
            else key: value
            for key, value in data_endurance_score.items()
        }

        data = {**data_hill_score, **data_endurance_score}

        return cls(**data)

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda d: d.calendar_date)
