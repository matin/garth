# Garth

[![CI](https://github.com/matin/garth/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](
    https://github.com/matin/garth/actions/workflows/ci.yml?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](
    https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](
    https://codecov.io/gh/matin/garth)
[![PyPI version](
    https://img.shields.io/pypi/v/garth.svg?logo=python&logoColor=brightgreen&color=brightgreen)](
    https://pypi.org/project/garth/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/garth)](
    https://pypistats.org/packages/garth)

Garmin SSO auth + Connect Python client

## Garmin Connect MCP Server

[`garth-mcp-server`](https://github.com/matin/garth-mcp-server) is in early development.
Contributions are greatly appreciated.

To generate your `GARTH_TOKEN`, use `uvx garth login`.
For China, do `uvx garth --domain garmin.cn login`.

## Google Colabs

### [Stress: 28-day rolling average](https://colab.research.google.com/github/matin/garth/blob/main/colabs/stress.ipynb)

Stress levels from one day to another can vary by extremes, but there's always
a general trend. Using a scatter plot with a rolling average shows both the
individual days and the trend. The Colab retrieves up to three years of daily
data. If there's less than three years of data, it retrieves whatever is
available.

![Stress: Garph of 28-day rolling average](
    https://github.com/matin/garth/assets/98985/868ecf25-4644-4879-b28f-ed0706a9e7b9)

### [Sleep analysis over 90 days](https://colab.research.google.com/github/matin/garth/blob/main/colabs/sleep.ipynb)

The Garmin Connect app only shows a maximum of seven days for sleep
stages—making it hard to see trends. The Connect API supports retrieving
daily sleep quality in 28-day pages, but that doesn't show details. Using
`SleedData.list()` gives us the ability to retrieve an arbitrary number of
day with enough detail to product a stacked bar graph of the daily sleep
stages.

![Sleep stages over 90 days](
    https://github.com/matin/garth/assets/98985/ba678baf-0c8a-4907-aa91-be43beec3090)

One specific graph that's useful but not available in the Connect app is
sleep start and end times over an extended period. This provides context
to the sleep hours and stages.

![Sleep times over 90 days](
    https://github.com/matin/garth/assets/98985/c5583b9e-ab8a-4b5c-bfe6-1cb0ca95d1de)

### [ChatGPT analysis of Garmin stats](https://colab.research.google.com/github/matin/garth/blob/main/colabs/chatgpt_analysis_of_stats.ipynb)

ChatGPT's Advanced Data Analysis took can provide incredible insight
into the data in a way that's much simpler than using Pandas and Matplotlib.

Start by using the linked Colab to download a CSV of the last three years
of your stats, and upload the CSV to ChatGPT.

Here's the outputs of the following prompts:

How do I sleep on different days of the week?

<img width="600" alt="image" src="https://github.com/matin/garth/assets/98985/b7507459-2482-43d6-bf55-c3a1f756facb">

On what days do I exercise the most?

<img width="600" alt="image" src="https://github.com/matin/garth/assets/98985/11294be2-8e1a-4fed-a489-13420765aada">

Magic!

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
1. OAuth1 token survives for a year
1. Supports MFA
1. Auto-refresh of OAuth2 token when expired
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

### Clone, setup environment and run tests

```bash
gh repo clone matin/garth
cd garth
make install
make
```

Use `make help` to see all the options.

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

### Custom MFA handler

By default, MFA will prompt for the code in the terminal. You can provide your
own handler:

```python
garth.login(email, password, prompt_mfa=lambda: input("Enter MFA code: "))
```

For advanced use cases (like async handling), MFA can be handled separately:

```python
result1, result2 = garth.login(email, password, return_on_mfa=True)
if result1 == "needs_mfa":  # MFA is required
    mfa_code = "123456"  # Get this from your custom MFA flow
    oauth1, oauth2 = garth.resume_login(result2, mfa_code)
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
from garth.exc import GarthException

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
    params={"date": "2023-07-05", "nonSleepBufferMinutes": 60},
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
stress = garth.connectapi("/usersummary-service/stats/stress/weekly/2023-07-05/52")
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

## Upload

```python
with open("12129115726_ACTIVITY.fit", "rb") as f:
    uploaded = garth.client.upload(f)
```

Note: Garmin doesn't accept uploads of _structured_ FIT files as outlined in
[this conversation](https://github.com/matin/garth/issues/27). FIT files
generated from workouts are accepted without issues.

```python
{
    'detailedImportResult': {
        'uploadId': 212157427938,
        'uploadUuid': {
            'uuid': '6e56051d-1dd4-4f2c-b8ba-00a1a7d82eb3'
        },
        'owner': 2591602,
        'fileSize': 5289,
        'processingTime': 36,
        'creationDate': '2023-09-29 01:58:19.113 GMT',
        'ipAddress': None,
        'fileName': '12129115726_ACTIVITY.fit',
        'report': None,
        'successes': [],
        'failures': []
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

### Body Battery

Daily Body Battery and stress data

```python
garth.DailyBodyBatteryStress.get("2023-07-20")
```

```python
DailyBodyBatteryStress(
    user_profile_pk=2591602,
    calendar_date=datetime.date(2023, 7, 20),
    start_timestamp_gmt=datetime.datetime(2023, 7, 20, 6, 0),
    end_timestamp_gmt=datetime.datetime(2023, 7, 21, 5, 59, 59, 999000),
    start_timestamp_local=datetime.datetime(2023, 7, 19, 23, 0),
    end_timestamp_local=datetime.datetime(2023, 7, 20, 22, 59, 59, 999000),
    max_stress_level=85,
    avg_stress_level=25,
    stress_chart_value_offset=0,
    stress_chart_y_axis_origin=0,
    stress_values_array=[
        [1689811800000, 12], [1689812100000, 18], [1689812400000, 15],
        [1689815700000, 45], [1689819300000, 85], [1689822900000, 35],
        [1689826500000, 20], [1689830100000, 15], [1689833700000, 25],
        [1689837300000, 30]
    ],
    body_battery_values_array=[
        [1689811800000, 'charging', 45, 1.0], [1689812100000, 'charging', 48, 1.0],
        [1689812400000, 'charging', 52, 1.0], [1689815700000, 'charging', 65, 1.0],
        [1689819300000, 'draining', 85, 1.0], [1689822900000, 'draining', 75, 1.0],
        [1689826500000, 'draining', 65, 1.0], [1689830100000, 'draining', 55, 1.0],
        [1689833700000, 'draining', 45, 1.0], [1689837300000, 'draining', 35, 1.0],
        [1689840900000, 'draining', 25, 1.0]
    ]
)

# Access derived properties
daily_bb = garth.DailyBodyBatteryStress.get("2023-07-20")
daily_bb.current_body_battery  # 25 (last reading)
daily_bb.max_body_battery      # 85
daily_bb.min_body_battery      # 25
daily_bb.body_battery_change   # -20 (45 -> 25)

# Access structured readings
for reading in daily_bb.body_battery_readings:
    print(f"Level: {reading.level}, Status: {reading.status}")
    # Level: 45, Status: charging
    # Level: 48, Status: charging
    # ... etc

for reading in daily_bb.stress_readings:
    print(f"Stress: {reading.stress_level}")
    # Stress: 12
    # Stress: 18
    # ... etc
```

Body Battery events (sleep events)

```python
garth.BodyBatteryData.get("2023-07-20")
```

```python
[
    BodyBatteryData(
        event=BodyBatteryEvent(
            event_type='sleep',
            event_start_time_gmt=datetime.datetime(2023, 7, 19, 21, 30),
            timezone_offset=-25200000,
            duration_in_milliseconds=28800000,
            body_battery_impact=35,
            feedback_type='good_sleep',
            short_feedback='Good sleep restored your Body Battery'
        ),
        activity_name=None,
        activity_type=None,
        activity_id=None,
        average_stress=15.5,
        stress_values_array=[
            [1689811800000, 12], [1689812100000, 18], [1689812400000, 15]
        ],
        body_battery_values_array=[
            [1689811800000, 'charging', 45, 1.0],
            [1689812100000, 'charging', 48, 1.0],
            [1689812400000, 'charging', 52, 1.0],
            [1689840600000, 'draining', 85, 1.0]
        ]
    )
]

# Access convenience properties on each event
events = garth.BodyBatteryData.get("2023-07-20")
event = events[0]
event.current_level    # 85 (last reading)
event.max_level        # 85
event.min_level        # 45
```

### Hydration

Daily hydration data

```python
garth.DailyHydration.list(period=2)
```

```python
[
    DailyHydration(
        calendar_date=datetime.date(2024, 6, 29),
        value_in_ml=1750.0,
        goal_in_ml=2800.0
    )
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

List sleep data over several nights.

```python
garth.SleepData.list("2023-07-20", 30)
```

### Weight

Retrieve the latest weight measurement and body composition data for a given
date.

**Note**: Weight, weight delta, bone mass, and muscle mass values are measured
in grams

```python
garth.WeightData.get("2025-06-01")
```

```python
WeightData(
    sample_pk=1749996902851,
    calendar_date=datetime.date(2025, 6, 15),
    weight=59720,
    source_type='INDEX_SCALE',
    weight_delta=200.00000000000284,
    timestamp_gmt=1749996876000,
    datetime_utc=datetime.datetime(2025, 6, 15, 14, 14, 36, tzinfo=TzInfo(UTC)),
    datetime_local=datetime.datetime(
        2025, 6, 15, 8, 14, 36,
        tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
    ),
    bmi=22.799999237060547,
    body_fat=19.3,
    body_water=58.9,
    bone_mass=3539,
    muscle_mass=26979,
    physique_rating=None,
    visceral_fat=None,
    metabolic_age=None
)
```

Get weight entries for a date range.

```python
garth.WeightData.list("2025-06-01", 30)
```

```python
[
    WeightData(
        sample_pk=1749307692871,
        calendar_date=datetime.date(2025, 6, 7),
        weight=59189,
        source_type='INDEX_SCALE',
        weight_delta=500.0,
        timestamp_gmt=1749307658000,
        datetime_utc=datetime.datetime(2025, 6, 7, 14, 47, 38, tzinfo=TzInfo(UTC)),
        datetime_local=datetime.datetime(
            2025, 6, 7, 8, 47, 38,
            tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
        ),
        bmi=22.600000381469727,
        body_fat=20.0,
        body_water=58.4,
        bone_mass=3450,
        muscle_mass=26850,
        physique_rating=None,
        visceral_fat=None,
        metabolic_age=None
    ),
    WeightData(
        sample_pk=1749909217098,
        calendar_date=datetime.date(2025, 6, 14),
        weight=59130,
        source_type='INDEX_SCALE',
        weight_delta=-100.00000000000142,
        timestamp_gmt=1749909180000,
        datetime_utc=datetime.datetime(2025, 6, 14, 13, 53, tzinfo=TzInfo(UTC)),
        datetime_local=datetime.datetime(
            2025, 6, 14, 7, 53,
            tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
        ),
        bmi=22.5,
        body_fat=20.3,
        body_water=58.2,
        bone_mass=3430,
        muscle_mass=26840,
        physique_rating=None,
        visceral_fat=None,
        metabolic_age=None
    ),
    WeightData(
        sample_pk=1749948744411,
        calendar_date=datetime.date(2025, 6, 14),
        weight=59500,
        source_type='MANUAL',
        weight_delta=399.9999999999986,
        timestamp_gmt=1749948725175,
        datetime_utc=datetime.datetime(
            2025, 6, 15, 0, 52, 5, 175000, tzinfo=TzInfo(UTC)
        ),
        datetime_local=datetime.datetime(
            2025, 6, 14, 18, 52, 5, 175000,
            tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
        ),
        bmi=None,
        body_fat=None,
        body_water=None,
        bone_mass=None,
        muscle_mass=None,
        physique_rating=None,
        visceral_fat=None,
        metabolic_age=None
    ),
    WeightData(
        sample_pk=1749996902851,
        calendar_date=datetime.date(2025, 6, 15),
        weight=59720,
        source_type='INDEX_SCALE',
        weight_delta=200.00000000000284,
        timestamp_gmt=1749996876000,
        datetime_utc=datetime.datetime(2025, 6, 15, 14, 14, 36, tzinfo=TzInfo(UTC)),
        datetime_local=datetime.datetime(
            2025, 6, 15, 8, 14, 36,
            tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
        ),
        bmi=22.799999237060547,
        body_fat=19.3,
        body_water=58.9,
        bone_mass=3539,
        muscle_mass=26979,
        physique_rating=None,
        visceral_fat=None,
        metabolic_age=None
    )
]
```

## User

### UserProfile

```python
garth.UserProfile.get()
```

```python
UserProfile(
    id=3154645,
    profile_id=2591602,
    garmin_guid="0690cc1d-d23d-4412-b027-80fd4ed1c0f6",
    display_name="mtamizi",
    full_name="Matin Tamizi",
    user_name="mtamizi",
    profile_image_uuid="73240e81-6e4d-43fc-8af8-c8f6c51b3b8f",
    profile_image_url_large=(
        "https://s3.amazonaws.com/garmin-connect-prod/profile_images/"
        "73240e81-6e4d-43fc-8af8-c8f6c51b3b8f-2591602.png"
    ),
    profile_image_url_medium=(
        "https://s3.amazonaws.com/garmin-connect-prod/profile_images/"
        "685a19e9-a7be-4a11-9bf9-faca0c5d1f1a-2591602.png"
    ),
    profile_image_url_small=(
        "https://s3.amazonaws.com/garmin-connect-prod/profile_images/"
        "6302f021-0ec7-4dc9-b0c3-d5a19bc5a08c-2591602.png"
    ),
    location="Ciudad de México, CDMX",
    facebook_url=None,
    twitter_url=None,
    personal_website=None,
    motivation=None,
    bio=None,
    primary_activity=None,
    favorite_activity_types=[],
    running_training_speed=0.0,
    cycling_training_speed=0.0,
    favorite_cycling_activity_types=[],
    cycling_classification=None,
    cycling_max_avg_power=0.0,
    swimming_training_speed=0.0,
    profile_visibility="private",
    activity_start_visibility="private",
    activity_map_visibility="public",
    course_visibility="public",
    activity_heart_rate_visibility="public",
    activity_power_visibility="public",
    badge_visibility="private",
    show_age=False,
    show_weight=False,
    show_height=False,
    show_weight_class=False,
    show_age_range=False,
    show_gender=False,
    show_activity_class=False,
    show_vo_2_max=False,
    show_personal_records=False,
    show_last_12_months=False,
    show_lifetime_totals=False,
    show_upcoming_events=False,
    show_recent_favorites=False,
    show_recent_device=False,
    show_recent_gear=False,
    show_badges=True,
    other_activity=None,
    other_primary_activity=None,
    other_motivation=None,
    user_roles=[
        "SCOPE_ATP_READ",
        "SCOPE_ATP_WRITE",
        "SCOPE_COMMUNITY_COURSE_READ",
        "SCOPE_COMMUNITY_COURSE_WRITE",
        "SCOPE_CONNECT_READ",
        "SCOPE_CONNECT_WRITE",
        "SCOPE_DT_CLIENT_ANALYTICS_WRITE",
        "SCOPE_GARMINPAY_READ",
        "SCOPE_GARMINPAY_WRITE",
        "SCOPE_GCOFFER_READ",
        "SCOPE_GCOFFER_WRITE",
        "SCOPE_GHS_SAMD",
        "SCOPE_GHS_UPLOAD",
        "SCOPE_GOLF_API_READ",
        "SCOPE_GOLF_API_WRITE",
        "SCOPE_INSIGHTS_READ",
        "SCOPE_INSIGHTS_WRITE",
        "SCOPE_PRODUCT_SEARCH_READ",
        "ROLE_CONNECTUSER",
        "ROLE_FITNESS_USER",
        "ROLE_WELLNESS_USER",
        "ROLE_OUTDOOR_USER",
        "ROLE_CONNECT_2_USER",
        "ROLE_TACX_APP_USER",
    ],
    name_approved=True,
    user_profile_full_name="Matin Tamizi",
    make_golf_scorecards_private=True,
    allow_golf_live_scoring=False,
    allow_golf_scoring_by_connections=True,
    user_level=3,
    user_point=118,
    level_update_date="2020-12-12T15:20:38.0",
    level_is_viewed=False,
    level_point_threshold=140,
    user_point_offset=0,
    user_pro=False,
)
```

### UserSettings

```python
garth.UserSettings.get()
```

```python
UserSettings(
    id=2591602,
    user_data=UserData(
        gender="MALE",
        weight=83000.0,
        height=182.0,
        time_format="time_twenty_four_hr",
        birth_date=datetime.date(1984, 10, 17),
        measurement_system="metric",
        activity_level=None,
        handedness="RIGHT",
        power_format=PowerFormat(
            format_id=30,
            format_key="watt",
            min_fraction=0,
            max_fraction=0,
            grouping_used=True,
            display_format=None,
        ),
        heart_rate_format=PowerFormat(
            format_id=21,
            format_key="bpm",
            min_fraction=0,
            max_fraction=0,
            grouping_used=False,
            display_format=None,
        ),
        first_day_of_week=FirstDayOfWeek(
            day_id=2,
            day_name="sunday",
            sort_order=2,
            is_possible_first_day=True,
        ),
        vo_2_max_running=45.0,
        vo_2_max_cycling=None,
        lactate_threshold_speed=0.34722125000000004,
        lactate_threshold_heart_rate=None,
        dive_number=None,
        intensity_minutes_calc_method="AUTO",
        moderate_intensity_minutes_hr_zone=3,
        vigorous_intensity_minutes_hr_zone=4,
        hydration_measurement_unit="milliliter",
        hydration_containers=[],
        hydration_auto_goal_enabled=True,
        firstbeat_max_stress_score=None,
        firstbeat_cycling_lt_timestamp=None,
        firstbeat_running_lt_timestamp=1044719868,
        threshold_heart_rate_auto_detected=True,
        ftp_auto_detected=None,
        training_status_paused_date=None,
        weather_location=None,
        golf_distance_unit="statute_us",
        golf_elevation_unit=None,
        golf_speed_unit=None,
        external_bottom_time=None,
    ),
    user_sleep=UserSleep(
        sleep_time=80400,
        default_sleep_time=False,
        wake_time=24000,
        default_wake_time=False,
    ),
    connect_date=None,
    source_type=None,
)
```

## Star History

<a href="https://www.star-history.com/#matin/garth&Date">
    <picture>
        <source
            media="(prefers-color-scheme: dark)"
            srcset="https://api.star-history.com/svg?repos=matin/garth&type=Date&theme=dark"
        />
        <source
            media="(prefers-color-scheme: light)"
            srcset="https://api.star-history.com/svg?repos=matin/garth&type=Date"
        />
    <img
        alt="Star History Chart"
        src="https://api.star-history.com/svg?repos=matin/garth&type=Date" />
    </picture>
</a>
