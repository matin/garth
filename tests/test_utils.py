from dataclasses import dataclass
from datetime import date, datetime

from garth.utils import (
    asdict,
    camel_to_snake,
    camel_to_snake_dict,
    format_end_date,
    remove_dto_suffix,
    remove_dto_suffix_from_dict,
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


def test_remove_dto_suffix():
    # Keys ending with _dto should have suffix removed
    assert remove_dto_suffix("activity_type_dto") == "activity_type"
    assert remove_dto_suffix("summary_dto") == "summary"
    assert remove_dto_suffix("event_type_dto") == "event_type"

    # Keys not ending with _dto should be unchanged
    assert remove_dto_suffix("activity_type") == "activity_type"
    assert remove_dto_suffix("activity_id") == "activity_id"
    assert remove_dto_suffix("dto_activity") == "dto_activity"
    assert remove_dto_suffix("") == ""


def test_remove_dto_suffix_from_dict():
    # Simple dict with _dto keys
    input_dict = {
        "activity_type_dto": {"type_id": 1, "type_key": "running"},
        "summary_dto": {"distance": 5000},
        "activity_id": 123,
    }
    expected = {
        "activity_type": {"type_id": 1, "type_key": "running"},
        "summary": {"distance": 5000},
        "activity_id": 123,
    }
    assert remove_dto_suffix_from_dict(input_dict) == expected

    # Nested dict with _dto keys
    input_dict = {
        "outer_dto": {
            "inner_dto": {"value": 1},
            "other": "data",
        }
    }
    expected = {
        "outer": {
            "inner": {"value": 1},
            "other": "data",
        }
    }
    assert remove_dto_suffix_from_dict(input_dict) == expected

    # List of dicts with _dto keys
    input_dict = {
        "items_dto": [
            {"item_dto": {"id": 1}},
            {"item_dto": {"id": 2}},
        ]
    }
    expected = {
        "items": [
            {"item": {"id": 1}},
            {"item": {"id": 2}},
        ]
    }
    assert remove_dto_suffix_from_dict(input_dict) == expected

    # Empty dict
    assert remove_dto_suffix_from_dict({}) == {}

    # Dict with no _dto keys
    input_dict = {"activity_id": 123, "name": "test"}
    assert remove_dto_suffix_from_dict(input_dict) == input_dict
