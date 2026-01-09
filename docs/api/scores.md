# Scores

Garmin scores and metrics including endurance score, hill score, VO2 max,
and morning training readiness.

!!! tip "Date defaults to today"
    All `.get()` and `.list()` methods accept an optional date parameter that
    defaults to today if not provided:
    ```python
    garth.GarminScoresData.get()  # Get today's scores
    ```

## Garmin Scores

### Get scores for single day

```python
garth.GarminScoresData.get("2025-07-07")
```

```python
GarminScoresData(
    user_profile_pk=131234790,
    calendar_date=datetime.date(2025, 7, 7),
    endurance_score=4820,
    endurance_classification=1,
    endurance_classification_lower_limit_elite=8800,
    endurance_classification_lower_limit_superior=8100,
    endurance_classification_lower_limit_expert=7300,
    endurance_classification_lower_limit_well_trained=6600,
    endurance_classification_lower_limit_trained=5800,
    endurance_classification_lower_limit_intermediate=5100,
    hill_score=20,
    hill_endurance_score=15,
    hill_strength_score=2,
    vo_2_max=48.0,
    vo_2_max_precise_value=48.0
)
```

### Get scores for date range

```python
garth.GarminScoresData.list("2025-07-07", 2)
```

```python
[
    GarminScoresData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 6),
        endurance_score=4820,
        endurance_classification=1,
        endurance_classification_lower_limit_elite=8800,
        endurance_classification_lower_limit_superior=8100,
        endurance_classification_lower_limit_expert=7300,
        endurance_classification_lower_limit_well_trained=6600,
        endurance_classification_lower_limit_trained=5800,
        endurance_classification_lower_limit_intermediate=5100,
        hill_score=20,
        hill_endurance_score=15,
        hill_strength_score=2,
        vo_2_max=48.0,
        vo_2_max_precise_value=48.0
    ),
    GarminScoresData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 7),
        endurance_score=4820,
        endurance_classification=1,
        endurance_classification_lower_limit_elite=8800,
        endurance_classification_lower_limit_superior=8100,
        endurance_classification_lower_limit_expert=7300,
        endurance_classification_lower_limit_well_trained=6600,
        endurance_classification_lower_limit_trained=5800,
        endurance_classification_lower_limit_intermediate=5100,
        hill_score=20,
        hill_endurance_score=15,
        hill_strength_score=2,
        vo_2_max=48.0,
        vo_2_max_precise_value=48.0
    )
]
```

## Morning Training Readiness

### Get readiness for single day

```python
garth.MorningTrainingReadinessData.get("2025-07-07")
```

```python
MorningTrainingReadinessData(
    user_profile_pk=131234790,
    calendar_date=datetime.date(2025, 7, 7),
    score=100,
    recovery_time=1.0,
    recovery_time_factor_feedback='GOOD',
    recovery_time_factor_percent=99,
    acute_load=20,
    hrv_factor_feedback='GOOD',
    hrv_factor_percent=92,
    hrv_weekly_average=53,
    sleep_history_factor_feedback='VERY_GOOD',
    sleep_history_factor_percent=92,
    sleep_score=80,
    sleep_score_factor_feedback='GOOD',
    sleep_score_factor_percent=70,
    stress_history_factor_feedback='GOOD',
    stress_history_factor_percent=72,
    feedback_short='READY_FOR_ACTION',
    timestamp=datetime.datetime(2025, 7, 7, 4, 0, 25),
    timestamp_local=datetime.datetime(2025, 7, 7, 6, 0, 25)
)
```

### Get readiness for date range

```python
garth.MorningTrainingReadinessData.list("2025-07-07", 2)
```

```python
[
    MorningTrainingReadinessData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 6),
        score=100,
        recovery_time=0.0,
        recovery_time_factor_feedback='VERY_GOOD',
        recovery_time_factor_percent=100,
        acute_load=24,
        hrv_factor_feedback='GOOD',
        hrv_factor_percent=89,
        hrv_weekly_average=53,
        sleep_history_factor_feedback='VERY_GOOD',
        sleep_history_factor_percent=92,
        sleep_score=91,
        sleep_score_factor_feedback='VERY_GOOD',
        sleep_score_factor_percent=91,
        stress_history_factor_feedback='GOOD',
        stress_history_factor_percent=79,
        feedback_short='READY_FOR_ACTION',
        timestamp=datetime.datetime(2025, 7, 6, 5, 59, 18),
        timestamp_local=datetime.datetime(2025, 7, 6, 7, 59, 18)
    ),
    MorningTrainingReadinessData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 7),
        score=100,
        recovery_time=1.0,
        recovery_time_factor_feedback='GOOD',
        recovery_time_factor_percent=99,
        acute_load=20,
        hrv_factor_feedback='GOOD',
        hrv_factor_percent=92,
        hrv_weekly_average=53,
        sleep_history_factor_feedback='VERY_GOOD',
        sleep_history_factor_percent=92,
        sleep_score=80,
        sleep_score_factor_feedback='GOOD',
        sleep_score_factor_percent=70,
        stress_history_factor_feedback='GOOD',
        stress_history_factor_percent=72,
        feedback_short='READY_FOR_ACTION',
        timestamp=datetime.datetime(2025, 7, 7, 4, 0, 25),
        timestamp_local=datetime.datetime(2025, 7, 7, 6, 0, 25)
    )
]
```
