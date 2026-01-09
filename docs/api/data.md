# Data

Data classes provide detailed, raw data for specific metrics including body battery,
heart rate, HRV readings, sleep stages, and weight measurements.

## Body Battery

### Daily Body Battery and stress data

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

### Body Battery events

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

## Heart Rate Data

### Daily heart rate

Retrieve heart rate data for a specific day, including resting heart rate,
min/max values, and time-series readings throughout the day.

```python
garth.DailyHeartRate.get("2024-01-15")
```

```python
DailyHeartRate(
    user_profile_pk=2591602,
    calendar_date=datetime.date(2024, 1, 15),
    start_timestamp_gmt=datetime.datetime(2024, 1, 15, 8, 0),
    end_timestamp_gmt=datetime.datetime(2024, 1, 16, 7, 59, 59),
    start_timestamp_local=datetime.datetime(2024, 1, 15, 0, 0),
    end_timestamp_local=datetime.datetime(2024, 1, 15, 23, 59, 59),
    max_heart_rate=145,
    min_heart_rate=48,
    resting_heart_rate=52,
    last_seven_days_avg_resting_heart_rate=51,
    heart_rate_values=[
        [1705305600000, 62], [1705305660000, 65], [1705305720000, 58],
        # ... time-series data throughout the day
    ],
    heart_rate_value_descriptors=None
)

# Access structured readings
hr = garth.DailyHeartRate.get("2024-01-15")
hr.resting_heart_rate           # 52
hr.max_heart_rate               # 145
hr.min_heart_rate               # 48
hr.last_seven_days_avg_resting_heart_rate  # 51

# Iterate over readings as HeartRateReading objects
for reading in hr.readings:
    print(f"{reading.timestamp}: {reading.heart_rate} bpm")
```

### List heart rate data

```python
garth.DailyHeartRate.list("2024-01-15", 7)
```

## HRV Data

### Detailed HRV data

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

## Sleep Data

### Detailed sleep data

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

### List sleep data

List sleep data over several nights:

```python
garth.SleepData.list("2023-07-20", 30)
```

## Weight Data

Retrieve the latest weight measurement and body composition data for a given date.

!!! note "Units"
    Weight, weight delta, bone mass, and muscle mass values are measured in grams.

### Get single day

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
    timestamp_local=1749975276000,
    bmi=22.799999237060547,
    body_fat=19.3,
    body_water=58.9,
    bone_mass=3539,
    muscle_mass=26979,
    physique_rating=None,
    visceral_fat=None,
    metabolic_age=None
)

# datetime_utc and datetime_local are available as properties:
# weight.datetime_utc -> datetime.datetime(2025, 6, 15, 14, 14, 36, tzinfo=UTC)
# weight.datetime_local -> datetime.datetime(2025, 6, 15, 8, 14, 36, tzinfo=...)
```

### Get date range

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
        timestamp_local=1749286058000,
        bmi=22.600000381469727,
        body_fat=20.0,
        body_water=58.4,
        bone_mass=3450,
        muscle_mass=26850,
        physique_rating=None,
        visceral_fat=None,
        metabolic_age=None
    ),
    # ... more entries
]

# datetime_utc and datetime_local are available as properties on each entry
```
