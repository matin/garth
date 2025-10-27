import dataclasses
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any


CAMEL_TO_SNAKE = re.compile(
    r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z])|(?<=[a-zA-Z])[0-9])"
)


def camel_to_snake(camel_str: str) -> str:
    snake_str = CAMEL_TO_SNAKE.sub(r"_\1", camel_str)
    return snake_str.lower()


def camel_to_snake_dict(camel_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Converts a dictionary's keys from camel case to snake case. This version
    handles nested dictionaries and lists.
    """
    snake_dict: dict[str, Any] = {}
    for k, v in camel_dict.items():
        new_key = camel_to_snake(k)
        if isinstance(v, dict):
            snake_dict[new_key] = camel_to_snake_dict(v)
        elif isinstance(v, list):
            snake_dict[new_key] = [
                camel_to_snake_dict(i) if isinstance(i, dict) else i for i in v
            ]
        else:
            snake_dict[new_key] = v
    return snake_dict


def format_end_date(end: date | str | None) -> date:
    if end is None:
        end = date.today()
    elif isinstance(end, str):
        end = date.fromisoformat(end)
    return end


def date_range(date_: date | str, days: int):
    date_ = date_ if isinstance(date_, date) else date.fromisoformat(date_)
    for day in range(days):
        yield date_ - timedelta(days=day)


def asdict(obj):
    if dataclasses.is_dataclass(obj):
        result = {}
        for field in dataclasses.fields(obj):
            value = getattr(obj, field.name)
            result[field.name] = asdict(value)
        return result

    if isinstance(obj, list):
        return [asdict(v) for v in obj]

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    return obj


def get_localized_datetime(
    gmt_timestamp: int, local_timestamp: int
) -> datetime:
    local_diff = local_timestamp - gmt_timestamp
    local_offset = timezone(timedelta(milliseconds=local_diff))
    gmt_time = datetime.fromtimestamp(gmt_timestamp / 1000, timezone.utc)
    return gmt_time.astimezone(local_offset)
