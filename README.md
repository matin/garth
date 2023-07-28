# Garth

[![CI](https://github.com/matin/garth/workflows/CI/badge.svg?event=push)](https://github.com/matin/garth/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](https://codecov.io/gh/matin/garth)

Garmin SSO auth + Connect client

## Google Colabs

[Graph 28-day rolling average of daily stress](https://colab.research.google.com/github/matin/garth/blob/main/colabs/stress.ipynb)


## Background

Garth is meant for personal use and follows the philosiphy that your data is
your data. You should be able to download it and analyze it in the way that
you'd like. In my case, that means processing with Google Colab, Pandas,
Matplotlib, etc.

There are already a few Garmin Connect libraries. Why write another?

### Authentication

The most important reasoning is to build a library with authentication that
works on [Google Colab](https://colab.research.google.com/) and doesn't require
tools like Cloudscraper. Garth, in comparison:

1. Uses the same embedded SSO as the mobile app
1. Only requires `requests` and `pydantic` as dependencies
1. Supports MFA
1. Supports saving and resuming sessions to avoid the need to log in each time
you run a script, which is particularly useful if you have MFA enabled
1. Works on Google Colab
1. Uses Pydantic dataclasses to validate and simplify use of data

### Python 3.10+

Google Colab, currently, uses 3.10. We should take advantage of all the goodies
that come along with it. If you need to use an earlier version of Python, there
are other libraries that will meet your needs. There's no intetion to backport.

### JSON vs HTML

Using `garth.connectapi()` allows you to make requests routed to the Connect API
and receive JSON vs needing to parse HTML. You can use the same endpoints the
mobile app uses.

This also goes back to authentication. Garth manages the necessary Bearer
Authentication (along with auto-refresh) necessary to make requests routed to
the Connect API.

## Instructions

### Install

```bash
python -m pip install garth
```

### Authenticate and save session

```python
import garth
from getpass import getpass

email = input("Enter email address: ")
password = getpass("Enter password: ")
# If there's MFA, you'll be prompted during the login
garth.login(email, password)

garth.save("~/.garth")
```

### Configure

#### Set domain for China

```python
garth.configure(domain="garmin.cn")
```

#### Proxy through Charles

```python
garth.configure(proxies={"https": "http://localhost:8888"}, ssl_verify=False)
```

### Attempt to resume session

```python
import garth
from garth import GarthException
from requests import HTTPError

garth.resume("~/.garth")
try:
    garth.client.auth_token.refresh()
except (GarthException, HTTPError):
    # Session is expired. You'll need to log in again
```

## Connect API

### Wellness

```python
sleep = garth.connectapi(
    f"/wellness-service/wellness/dailySleepData/{garth.client.username}",
    params={"date": "2023-07-05", "nonSleepBufferMinutes": 60),
)
list(sleep.keys())
```

```json
[
    "dailySleepDTO",
    "sleepMovement",
    "remSleepData",
    "sleepLevels",
    "sleepRestlessMoments",
    "restlessMomentsCount",
    "wellnessSpO2SleepSummaryDTO",
    "wellnessEpochSPO2DataDTOList",
    "wellnessEpochRespirationDataDTOList",
    "sleepStress"
]
```

### Usersummary

```python
stress =  garth.connectapi(f"/usersummary-service/stats/stress/weekly/2023-07-05/52")
```

```json
{
    "calendarDate": "2023-07-13",
    "values": {
        "highStressDuration": 2880,
        "lowStressDuration": 10140,
        "overallStressLevel": 33,
        "restStressDuration": 30960,
        "mediumStressDuration": 8760
    }
}
```

## Resources

### Stress

Daily stress levels

```python
DailyStress.list("2023-07-23", 2)
```

```python
[
    DailyStress(
        calendar_date=datetime.date(2023, 7, 22),
        overall_stress_level=31,
        rest_stress_duration=31980,
        low_stress_duration=23820,
        medium_stress_duration=7440,
        high_stress_duration=1500
    ),
    DailyStress(
        calendar_date=datetime.date(2023, 7, 23),
        overall_stress_level=26,
        rest_stress_duration=38220,
        low_stress_duration=22500,
        medium_stress_duration=2520,
        high_stress_duration=300
    )
]
```

Weekly stress levels

```python
WeeklyStress.list("2023-07-23", 2)
```

```python
[
    WeeklyStress(calendar_date=datetime.date(2023, 7, 10), value=33),
    WeeklyStress(calendar_date=datetime.date(2023, 7, 17), value=32)
]
```

### Sleep

Daily sleep quality

```python
garth.DailySleep.list("2023-07-23", 2)
```

```python
[
    DailySleep(calendar_date=datetime.date(2023, 7, 22), value=69),
    DailySleep(calendar_date=datetime.date(2023, 7, 23), value=73)
]
```


Detailed sleep data

```python
garth.SleepData.get("2023-07-20")
```

```python
SleepData(
    daily_sleep_dto=DailySleepDTO(
        id=1689830700000,
        user_profile_pk=2591602,
        calendar_date=datetime.date(2023, 7, 20),
        sleep_time_seconds=23700,
        nap_time_seconds=0,
        sleep_window_confirmed=True,
        sleep_window_confirmation_type='enhanced_confirmed_final',
        sleep_start_timestamp_gmt=datetime.datetime(2023, 7, 20, 5, 25, tzinfo=TzInfo(UTC)),
        sleep_end_timestamp_gmt=datetime.datetime(2023, 7, 20, 12, 11, tzinfo=TzInfo(UTC)),
        sleep_start_timestamp_local=datetime.datetime(2023, 7, 19, 23, 25, tzinfo=TzInfo(UTC)),
        sleep_end_timestamp_local=datetime.datetime(2023, 7, 20, 6, 11, tzinfo=TzInfo(UTC)),
        unmeasurable_sleep_seconds=0,
        deep_sleep_seconds=9660,
        light_sleep_seconds=12600,
        rem_sleep_seconds=1440,
        awake_sleep_seconds=660,
        device_rem_capable=True,
        retro=False,
        sleep_from_device=True,
        sleep_version=2,
        awake_count=1,
        sleep_scores=SleepScores(
            total_duration=Score(
                qualifier_key='FAIR',
                optimal_start=28800.0,
                optimal_end=28800.0,
                value=None,
                ideal_start_in_seconds=None,
                deal_end_in_seconds=None
            ),
            stress=Score(
                qualifier_key='FAIR',
                optimal_start=0.0,
                optimal_end=15.0,
                value=None,
                ideal_start_in_seconds=None,
                ideal_end_in_seconds=None
            ),
            awake_count=Score(
                qualifier_key='GOOD',
                optimal_start=0.0,
                optimal_end=1.0,
                value=None,
                ideal_start_in_seconds=None,
                ideal_end_in_seconds=None
            ),
            overall=Score(
                qualifier_key='FAIR',
                optimal_start=None,
                optimal_end=None,
                value=68,
                ideal_start_in_seconds=None,
                ideal_end_in_seconds=None
            ),
            rem_percentage=Score(
                qualifier_key='POOR',
                optimal_start=21.0,
                optimal_end=31.0,
                value=6,
                ideal_start_in_seconds=4977.0,
                ideal_end_in_seconds=7347.0
            ),
            restlessness=Score(
                qualifier_key='EXCELLENT',
                optimal_start=0.0,
                optimal_end=5.0,
                value=None,
                ideal_start_in_seconds=None,
                ideal_end_in_seconds=None
            ),
            light_percentage=Score(
                qualifier_key='EXCELLENT',
                optimal_start=30.0,
                optimal_end=64.0,
                value=53,
                ideal_start_in_seconds=7110.0,
                ideal_end_in_seconds=15168.0
            ),
            deep_percentage=Score(
                qualifier_key='EXCELLENT',
                optimal_start=16.0,
                optimal_end=33.0,
                value=41,
                ideal_start_in_seconds=3792.0,
                ideal_end_in_seconds=7821.0
            )
        ),
        auto_sleep_start_timestamp_gmt=None,
        auto_sleep_end_timestamp_gmt=None,
        sleep_quality_type_pk=None,
        sleep_result_type_pk=None,
        average_sp_o2_value=92.0,
        lowest_sp_o2_value=87,
        highest_sp_o2_value=100,
        average_sp_o2_hr_sleep=53.0,
        average_respiration_value=14.0,
        lowest_respiration_value=12.0,
        highest_respiration_value=16.0,
        avg_sleep_stress=17.0,
        age_group='ADULT',
        sleep_score_feedback='NEGATIVE_NOT_ENOUGH_REM',
        sleep_score_insight='NONE'
    ),
    sleep_movement=[
        SleepMovement(
            start_gmt=datetime.datetime(2023, 7, 20, 4, 25),
            end_gmt=datetime.datetime(2023, 7, 20, 4, 26),
            activity_level=5.688743692980419
        ),
        SleepMovement(
            start_gmt=datetime.datetime(2023, 7, 20, 4, 26),
            end_gmt=datetime.datetime(2023, 7, 20, 4, 27),
            activity_level=5.318763075304898
        ),
        ...,
        SleepMovement(
            start_gmt=datetime.datetime(2023, 7, 20, 13, 10),
            end_gmt=datetime.datetime(2023, 7, 20, 13, 11),
            activity_level=7.088729101943337
        )
    ]
)
```

leep data over several nights

```python
garth.SleepData.get(end="2023-07-20", days=30)
```
