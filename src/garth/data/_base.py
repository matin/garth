import builtins
from abc import ABC, abstractmethod
from datetime import date
from itertools import chain

from typing_extensions import Self

from .. import http
from ..utils import date_range, format_end_date

# Kept for backward compatibility — thread pool is no longer used
# since browser transport cannot be called from multiple threads.
MAX_WORKERS = 1


class Data(ABC):
    @classmethod
    @abstractmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> Self | builtins.list[Self] | None: ...

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        days: int = 1,
        *,
        client: http.Client | None = None,
        max_workers: int = 1,
    ) -> builtins.list[Self]:
        """Fetch data for multiple dates sequentially.

        Note:
            The max_workers parameter is accepted for backward
            compatibility but ignored. All requests go through a
            single browser page and cannot be parallelized.
        """
        client = client or http.client
        end = format_end_date(end)

        dates = date_range(end, days)
        data = []
        for date_ in dates:
            day = cls.get(date_, client=client)
            if day is not None:
                data.append(day)

        return list(
            chain.from_iterable(
                day if isinstance(day, list) else [day]
                for day in data
            )
        )
