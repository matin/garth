from datetime import date, timedelta
from typing import ClassVar

from pydantic.dataclasses import dataclass

from . import http
from .utils import camel_to_snake_dict, format_end_date

BASE_PATH = "/usersummary-service/stats/stress"


@dataclass(frozen=True)
class Stats:
    calendar_date: date

    _path: ClassVar[str]
    _page_size: ClassVar[int]

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 1,
        *,
        client: http.Client | None = None,
    ) -> list["Stats"]:
        client = client or http.client
        end = format_end_date(end)
        period_type = "days" if "daily" in cls._path else "weeks"

        if period > cls._page_size:
            page = cls.list(end, cls._page_size, client=client)
            if not page:
                return []
            page = (
                cls.list(
                    end - timedelta(**{period_type: cls._page_size}),
                    period - cls._page_size,
                    client=client,
                )
                + page
            )
            return page

        if period_type == "weeks":
            path = f"{cls._path}/{end}/{period}"
        else:
            start = end - timedelta(**{period_type: period - 1})
            path = f"{cls._path}/{start}/{end}"
        page_dirs = client.connectapi(path)
        if page_dirs and "values" in page_dirs[0]:
            page_dirs = [stat | stat.pop("values") for stat in page_dirs]
        page_dirs = [camel_to_snake_dict(stat) for stat in page_dirs]
        return [cls(**stat) for stat in page_dirs]
