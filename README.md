# Garth

[![CI](https://github.com/matin/garth/workflows/CI/badge.svg?event=push)](https://github.com/matin/garth/actions/workflows/ci.yml?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](https://codecov.io/gh/matin/garth)

Garmin SSO auth + Connect Python client

## Google Colabs

### [Stress: 28-day rolling average](https://colab.research.google.com/github/matin/garth/blob/main/colabs/stress.ipynb)

Stress levels from one day to another can vary by extremes, but there's always
a general trend. Using a scatter plot with a rolling average shows both the
individual days and the trend. The Colab retrieves up to three years of daily
data. If there's less than three years of data, it retrieves whatever is
available.

![Stress: Garph of 28-day rolling average](https://github.com/matin/garth/assets/98985/868ecf25-4644-4879-b28f-ed0706a9e7b9)

### [Sleep analysis over 90 days](https://colab.research.google.com/github/matin/garth/blob/main/colabs/sleep.ipynb)

The Garmin Connect app only shows a maximum of seven days for sleep
stages—making it hard to see trends. The Connect API supports retrieving
daily sleep quality in 28-day pages, but that doesn't show details. Using
`SleedData.list()` gives us the ability to retrieve an arbitrary number of
day with enough detail to product a stacked bar graph of the daily sleep
stages.

![Sleep stages over 90 days](https://github.com/matin/garth/assets/98985/ba678baf-0c8a-4907-aa91-be43beec3090)

One specific graph that's useful but not available in the Connect app is
sleep start and end times over an extended period. This provides context
to the sleep hours and stages.

![Sleep times over 90 days](https://github.com/matin/garth/assets/98985/c5583b9e-ab8a-4b5c-bfe6-1cb0ca95d1de)

## Background

Garth is meant for personal use and follows the philosophy that your data is
your data. You should be able to download it and analyze it in the way that
you'd like. In my case, that means processing with Google Colab, Pandas,
Matplotlib, etc.

There are already a few Garmin Connect libraries. Why write another?

### Authentication and stability

The most important reasoning is to build a library with authentication that
works on [Google Colab](https://colab.research.google.com/) and doesn't require
tools like Cloudscraper. Garth, in comparison:

1. Uses OAuth1 and OAuth2 token authentication after initial login
1. OAuth tokens survive for a year
1. Supports MFA
1. Auto-refresh of OAuth2 token when expired
1. OAuth1 token is valid for one year
1. Works on Google Colab
1. Uses Pydantic dataclasses to validate and simplify use of data
1. Full test coverage

### JSON vs HTML

Using `garth.connectapi()` allows you to make requests to the Connect API
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

garth.resume("~/.garth")
try:
    garth.client.username
except GarthException:
    # Session is expired. You'll need to log in again
```

## Connect API

### Daily details

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

### Stats

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

## Stats resources

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

### Steps

Daily steps

```python
garth.DailySteps.list(period=2)
```

```python
[
    DailySteps(
        calendar_date=datetime.date(2023, 7, 28),
        total_steps=6510,
        total_distance=5552,
        step_goal=8090
    ),
    DailySteps(
        calendar_date=datetime.date(2023, 7, 29),
        total_steps=7218,
        total_distance=6002,
        step_goal=7940
    )
]
```

Weekly steps

```python
garth.WeeklySteps.list(period=2)
```

```python
[
    WeeklySteps(
        calendar_date=datetime.date(2023, 7, 16),
        total_steps=42339,
        average_steps=6048.428571428572,
        average_distance=5039.285714285715,
        total_distance=35275.0,
        wellness_data_days_count=7
    ),
    WeeklySteps(
        calendar_date=datetime.date(2023, 7, 23),
        total_steps=56420,
        average_steps=8060.0,
        average_distance=7198.142857142857,
        total_distance=50387.0,
        wellness_data_days_count=7
    )
]
```

### Intensity Minutes

Daily intensity minutes

```python
garth.DailyIntensityMinutes.list(period=2)
```

```python
[
    DailyIntensityMinutes(
        calendar_date=datetime.date(2023, 7, 28),
        weekly_goal=150,
        moderate_value=0,
        vigorous_value=0
    ),
    DailyIntensityMinutes(
        calendar_date=datetime.date(2023, 7, 29),
        weekly_goal=150,
        moderate_value=0,
        vigorous_value=0
    )
]
```

Weekly intensity minutes

```python
garth.WeeklyIntensityMinutes.list(period=2)
```

```python
[
    WeeklyIntensityMinutes(
        calendar_date=datetime.date(2023, 7, 17),
        weekly_goal=150,
        moderate_value=103,
        vigorous_value=9
    ),
    WeeklyIntensityMinutes(
        calendar_date=datetime.date(2023, 7, 24),
        weekly_goal=150,
        moderate_value=101,
        vigorous_value=105
    )
]
```

### HRV

Daily HRV

```python
garth.DailyHRV.list(period=2)
```

```python
[
    DailyHRV(
        calendar_date=datetime.date(2023, 7, 28),
        weekly_avg=39,
        last_night_avg=36,
        last_night_5_min_high=52,
        baseline=HRVBaseline(
            low_upper=36,
            balanced_low=39,
            balanced_upper=51,
            marker_value=0.25
        ),
        status='BALANCED',
        feedback_phrase='HRV_BALANCED_2',
        create_time_stamp=datetime.datetime(2023, 7, 28, 12, 40, 16, 785000)
    ),
    DailyHRV(
        calendar_date=datetime.date(2023, 7, 29),
        weekly_avg=40,
        last_night_avg=41,
        last_night_5_min_high=76,
        baseline=HRVBaseline(
            low_upper=36,
            balanced_low=39,
            balanced_upper=51,
            marker_value=0.2916565
        ),
        status='BALANCED',
        feedback_phrase='HRV_BALANCED_8',
        create_time_stamp=datetime.datetime(2023, 7, 29, 13, 45, 23, 479000)
    )
]
```

Detailed HRV data

```python
garth.HRVData.get("2023-07-20")
```

```python
HRVData(
    user_profile_pk=2591602,
    hrv_summary=HRVSummary(
        calendar_date=datetime.date(2023, 7, 20),
        weekly_avg=39,
        last_night_avg=42,
        last_night_5_min_high=66,
        baseline=Baseline(
            low_upper=36,
            balanced_low=39,
            balanced_upper=52,
            marker_value=0.25
        ),
        status='BALANCED',
        feedback_phrase='HRV_BALANCED_7',
        create_time_stamp=datetime.datetime(2023, 7, 20, 12, 14, 11, 898000)
    ),
    hrv_readings=[
        HRVReading(
            hrv_value=54,
            reading_time_gmt=datetime.datetime(2023, 7, 20, 5, 29, 48),
            reading_time_local=datetime.datetime(2023, 7, 19, 23, 29, 48)
        ),
        HRVReading(
            hrv_value=56,
            reading_time_gmt=datetime.datetime(2023, 7, 20, 5, 34, 48),
            reading_time_local=datetime.datetime(2023, 7, 19, 23, 34, 48)
        ),
        # ... truncated for brevity
        HRVReading(
            hrv_value=38,
            reading_time_gmt=datetime.datetime(2023, 7, 20, 12, 9, 48),
            reading_time_local=datetime.datetime(2023, 7, 20, 6, 9, 48)
        )
    ],
    start_timestamp_gmt=datetime.datetime(2023, 7, 20, 5, 25),
    end_timestamp_gmt=datetime.datetime(2023, 7, 20, 12, 9, 48),
    start_timestamp_local=datetime.datetime(2023, 7, 19, 23, 25),
    end_timestamp_local=datetime.datetime(2023, 7, 20, 6, 9, 48),
    sleep_start_timestamp_gmt=datetime.datetime(2023, 7, 20, 5, 25),
    sleep_end_timestamp_gmt=datetime.datetime(2023, 7, 20, 12, 11),
    sleep_start_timestamp_local=datetime.datetime(2023, 7, 19, 23, 25),
    sleep_end_timestamp_local=datetime.datetime(2023, 7, 20, 6, 11)
)
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
        # ... truncated for brevity
        SleepMovement(
            start_gmt=datetime.datetime(2023, 7, 20, 13, 10),
            end_gmt=datetime.datetime(2023, 7, 20, 13, 11),
            activity_level=7.088729101943337
        )
    ]
)
```

sleep data over several nights

```python
garth.SleepData.list("2023-07-20", 30)
```
