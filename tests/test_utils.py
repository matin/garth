from datetime import date

from garth.utils import camel_to_snake, camel_to_snake_dict, format_end_date


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
