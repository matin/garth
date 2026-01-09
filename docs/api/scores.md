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
    user_profile_pk=2591602,
    calendar_date=datetime.date(2025, 7, 7),
    score=80,
    recovery_time=1.0,
    recovery_time_factor_feedback='GOOD',
    recovery_time_factor_percent=99,
    acute_load=351,
    hrv_factor_feedback='GOOD',
    hrv_factor_percent=99,
    hrv_weekly_average=42,
    sleep_history_factor_feedback='GOOD',
    sleep_history_factor_percent=80,
    sleep_score=83,
    sleep_score_factor_feedback='GOOD',
    sleep_score_factor_percent=76,
    stress_history_factor_feedback='GOOD',
    stress_history_factor_percent=84,
    feedback_short='WELL_RECOVERED',
    timestamp=datetime.datetime(2025, 7, 7, 11, 45, 17),
    timestamp_local=datetime.datetime(2025, 7, 7, 5, 45, 17)
)
```

### Get readiness for date range

```python
garth.MorningTrainingReadinessData.list("2025-07-07", 2)
```

```python
[
    MorningTrainingReadinessData(
        user_profile_pk=2591602,
        calendar_date=datetime.date(2025, 7, 6),
        score=66,
        recovery_time=563.0,
        recovery_time_factor_feedback='GOOD',
        recovery_time_factor_percent=85,
        acute_load=420,
        hrv_factor_feedback='VERY_GOOD',
        hrv_factor_percent=100,
        hrv_weekly_average=43,
        sleep_history_factor_feedback='GOOD',
        sleep_history_factor_percent=78,
        sleep_score=83,
        sleep_score_factor_feedback='GOOD',
        sleep_score_factor_percent=76,
        stress_history_factor_feedback='GOOD',
        stress_history_factor_percent=74,
        feedback_short='RECOVERED_AND_READY',
        timestamp=datetime.datetime(2025, 7, 6, 12, 22, 28),
        timestamp_local=datetime.datetime(2025, 7, 6, 6, 22, 28)
    ),
    MorningTrainingReadinessData(
        user_profile_pk=2591602,
        calendar_date=datetime.date(2025, 7, 7),
        score=80,
        recovery_time=1.0,
        recovery_time_factor_feedback='GOOD',
        recovery_time_factor_percent=99,
        acute_load=351,
        hrv_factor_feedback='GOOD',
        hrv_factor_percent=99,
        hrv_weekly_average=42,
        sleep_history_factor_feedback='GOOD',
        sleep_history_factor_percent=80,
        sleep_score=83,
        sleep_score_factor_feedback='GOOD',
        sleep_score_factor_percent=76,
        stress_history_factor_feedback='GOOD',
        stress_history_factor_percent=84,
        feedback_short='WELL_RECOVERED',
        timestamp=datetime.datetime(2025, 7, 7, 11, 45, 17),
        timestamp_local=datetime.datetime(2025, 7, 7, 5, 45, 17)
    )
]
```

## Training Readiness (All Entries)

While `MorningTrainingReadinessData` returns only the morning readiness snapshot,
`TrainingReadinessData` returns all training readiness entries for a day,
including post-exercise updates and realtime variable updates.

### Get all entries for single day

```python
garth.TrainingReadinessData.get("2025-07-07")
```

```python
[
    TrainingReadinessData(
        user_profile_pk=2591602,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 7, 8, 50, 17),
        timestamp_local=datetime.datetime(2025, 7, 7, 2, 50, 17),
        device_id=3469703076,
        level='HIGH',
        feedback_long='HIGH_RT_AVAILABLE_SS_UNKNOWN',
        feedback_short='WELL_RECOVERED',
        score=75,
        sleep_score=None,
        sleep_score_factor_percent=0,
        sleep_score_factor_feedback='NONE',
        recovery_time=0.0,
        recovery_time_factor_percent=100,
        recovery_time_factor_feedback='VERY_GOOD',
        acwr_factor_percent=90,
        acwr_factor_feedback='GOOD',
        acute_load=420,
        stress_history_factor_percent=74,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=98,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=43,
        sleep_history_factor_percent=80,
        sleep_history_factor_feedback='GOOD',
        valid_sleep=False,
        input_context='UPDATE_REALTIME_VARIABLES',
        primary_activity_tracker=True,
        recovery_time_change_phrase=None
    ),
    TrainingReadinessData(
        user_profile_pk=2591602,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 7, 11, 45, 17),
        timestamp_local=datetime.datetime(2025, 7, 7, 5, 45, 17),
        device_id=3469703076,
        level='HIGH',
        feedback_long='HIGH_RT_HIGHEST_SS_AVAILABLE',
        feedback_short='WELL_RECOVERED',
        score=80,
        sleep_score=83,
        sleep_score_factor_percent=76,
        sleep_score_factor_feedback='GOOD',
        recovery_time=1.0,
        recovery_time_factor_percent=99,
        recovery_time_factor_feedback='GOOD',
        acwr_factor_percent=90,
        acwr_factor_feedback='GOOD',
        acute_load=351,
        stress_history_factor_percent=84,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=99,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=42,
        sleep_history_factor_percent=80,
        sleep_history_factor_feedback='GOOD',
        valid_sleep=True,
        input_context='AFTER_WAKEUP_RESET',
        primary_activity_tracker=True,
        recovery_time_change_phrase='NO_CHANGE_SLEEP'
    ),
    TrainingReadinessData(
        user_profile_pk=2591602,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 7, 14, 57, 5),
        timestamp_local=datetime.datetime(2025, 7, 7, 8, 57, 5),
        device_id=3469703076,
        level='LOW',
        feedback_long='LOW_RT_HIGH_SS_GOOD_OR_MOD',
        feedback_short='HIGH_RECOVERY_NEEDS',
        score=32,
        sleep_score=83,
        sleep_score_factor_percent=76,
        sleep_score_factor_feedback='GOOD',
        recovery_time=2777.0,
        recovery_time_factor_percent=32,
        recovery_time_factor_feedback='POOR',
        acwr_factor_percent=70,
        acwr_factor_feedback='GOOD',
        acute_load=583,
        stress_history_factor_percent=84,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=99,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=42,
        sleep_history_factor_percent=80,
        sleep_history_factor_feedback='GOOD',
        valid_sleep=True,
        input_context='AFTER_POST_EXERCISE_RESET',
        primary_activity_tracker=True,
        recovery_time_change_phrase='NEW_EXERCISE'
    )
]
```

### Filter by input context

```python
entries = garth.TrainingReadinessData.get("2025-07-07")
morning = next(e for e in entries if e.input_context == "AFTER_WAKEUP_RESET")
post_exercise = [e for e in entries if e.input_context == "AFTER_POST_EXERCISE_RESET"]
```
