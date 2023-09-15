from datetime import date, datetime, timedelta
from typing import ClassVar, List, Optional, Union

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


@dataclass(frozen=True)
class HRVBaseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float


@dataclass(frozen=True)
class DailyHRV:
    calendar_date: date
    weekly_avg: int
    last_night_avg: int
    last_night_5_min_high: int
    baseline: HRVBaseline
    status: str
    feedback_phrase: str
    create_time_stamp: datetime

    _path: ClassVar[str] = "/hrv-service/hrv/daily/{start}/{end}"
    _page_size: ClassVar[int] = 28

    @classmethod
    def list(
        cls,
        end: Union[date, str, None] = None,
        period: int = 28,
        *,
        client: Optional[http.Client] = None,
    ) -> List["DailyHRV"]:
        client = client or http.client
        end = format_end_date(end)

        # Paginate if period is greater than page size
        if period > cls._page_size:
            page = cls.list(end, cls._page_size, client=client)
            if not page:
                return []
            page = (
                cls.list(
                    end - timedelta(days=cls._page_size),
                    period - cls._page_size,
                    client=client,
                )
                + page
            )
            return page

        start = end - timedelta(days=period - 1)
        path = cls._path.format(start=start, end=end)
        daily_hrv = client.connectapi(path)
        if daily_hrv is None:
            return []
        daily_hrv = camel_to_snake_dict(daily_hrv)["hrv_summaries"]
        assert daily_hrv
        return [cls(**hrv) for hrv in daily_hrv]
