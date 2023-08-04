from dataclasses import dataclass
from datetime import date, datetime

from garth.utils import (
    asdict,
    camel_to_snake,
    camel_to_snake_dict,
    format_end_date,
)


def test_camel_to_snake():
    assert camel_to_snake("hiThereHuman") == "hi_there_human"


def test_camel_to_snake_dict():
    assert camel_to_snake_dict({"hiThereHuman": "hi"}) == {
        "hi_there_human": "hi"
    }


def test_format_end_date():
    assert format_end_date("2021-01-01") == date(2021, 1, 1)
    assert format_end_date(None) == date.today()
    assert format_end_date(date(2021, 1, 1)) == date(2021, 1, 1)


@dataclass
class AsDictTestClass:
    name: str
    age: int
    birth_date: date


def test_asdict():
    # Test for dataclass instance
    instance = AsDictTestClass("Test", 20, date.today())
    assert asdict(instance) == {
        "name": "Test",
        "age": 20,
        "birth_date": date.today().isoformat(),
    }

    # Test for list of dataclass instances
    instances = [
        AsDictTestClass("Test1", 20, date.today()),
        AsDictTestClass("Test2", 30, date.today()),
    ]
    expected_output = [
        {"name": "Test1", "age": 20, "birth_date": date.today().isoformat()},
        {"name": "Test2", "age": 30, "birth_date": date.today().isoformat()},
    ]
    assert asdict(instances) == expected_output

    # Test for date instance
    assert asdict(date.today()) == date.today().isoformat()

    # Test for datetime instance
    now = datetime.now()
    assert asdict(now) == now.isoformat()

    # Test for regular types
    assert asdict("Test") == "Test"
    assert asdict(123) == 123
    assert asdict(None) is None
