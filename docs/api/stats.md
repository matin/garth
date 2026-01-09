# Stats

Stats provide aggregated daily and weekly summaries of various health metrics.

!!! tip "Date defaults to today"
    All `.list()` methods accept an optional date parameter that defaults to
    today if not provided:
    ```python
    garth.DailySteps.list(period=7)  # Last 7 days ending today
    ```

## Stress

### Daily stress levels

```python
garth.DailyStress.list("2023-07-23", 2)
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

### Weekly stress levels

```python
garth.WeeklyStress.list("2023-07-23", 2)
```

```python
[
    WeeklyStress(calendar_date=datetime.date(2023, 7, 10), value=33),
    WeeklyStress(calendar_date=datetime.date(2023, 7, 17), value=32)
]
```

## Hydration

### Daily hydration data

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

### Log hydration intake

```python
garth.DailyHydration.log(500)  # Log 500ml now
```

```python
HydrationLogEntry(
    user_id=2591602,
    calendar_date=datetime.date(2026, 1, 9),
    value_in_ml=1000.0,
    last_entry_timestamp_local=datetime.datetime(2026, 1, 9, 15, 30),
    goal_in_ml=3382.0,
    sweat_loss_in_ml=582.0,
    activity_intake_in_ml=0.0
)
```

Log with a specific timestamp:

```python
garth.DailyHydration.log(500, timestamp=datetime.datetime(2026, 1, 9, 15, 30))
```

## Steps

### Daily steps

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

### Weekly steps

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

## Intensity Minutes

### Daily intensity minutes

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

### Weekly intensity minutes

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

## HRV

### Daily HRV

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

## Sleep Quality

### Daily sleep quality

```python
garth.DailySleep.list("2023-07-23", 2)
```

```python
[
    DailySleep(calendar_date=datetime.date(2023, 7, 22), value=69),
    DailySleep(calendar_date=datetime.date(2023, 7, 23), value=73)
]
```
