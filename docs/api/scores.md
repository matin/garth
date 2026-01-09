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
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 6, 22, 39, 28),
        timestamp_local=datetime.datetime(2025, 7, 7, 0, 39, 28),
        device_id=3477316333,
        level='HIGH',
        feedback_long='HIGH_RT_AVAILABLE_SS_UNKNOWN_ACWR_POS',
        feedback_short='WELL_RECOVERED',
        score=94,
        sleep_score=None,
        sleep_score_factor_percent=0,
        sleep_score_factor_feedback='NONE',
        recovery_time=0.0,
        recovery_time_factor_percent=100,
        recovery_time_factor_feedback='VERY_GOOD',
        acwr_factor_percent=100,
        acwr_factor_feedback='VERY_GOOD',
        acute_load=24,
        stress_history_factor_percent=79,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=87,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=53,
        sleep_history_factor_percent=92,
        sleep_history_factor_feedback='VERY_GOOD',
        valid_sleep=False,
        input_context='UPDATE_REALTIME_VARIABLES',
        primary_activity_tracker=True,
        recovery_time_change_phrase=None
    ),
    TrainingReadinessData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 7, 4, 0, 25),
        timestamp_local=datetime.datetime(2025, 7, 7, 6, 0, 25),
        device_id=3477316333,
        level='PRIME',
        feedback_long='PRIME_RT_HIGHEST_SS_AVAILABLE_ACWR_POS',
        feedback_short='READY_FOR_ACTION',
        score=100,
        sleep_score=80,
        sleep_score_factor_percent=70,
        sleep_score_factor_feedback='GOOD',
        recovery_time=1.0,
        recovery_time_factor_percent=99,
        recovery_time_factor_feedback='GOOD',
        acwr_factor_percent=100,
        acwr_factor_feedback='VERY_GOOD',
        acute_load=20,
        stress_history_factor_percent=72,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=92,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=53,
        sleep_history_factor_percent=92,
        sleep_history_factor_feedback='VERY_GOOD',
        valid_sleep=True,
        input_context='AFTER_WAKEUP_RESET',
        primary_activity_tracker=True,
        recovery_time_change_phrase='NO_CHANGE_SLEEP'
    ),
    TrainingReadinessData(
        user_profile_pk=131234790,
        calendar_date=datetime.date(2025, 7, 7),
        timestamp=datetime.datetime(2025, 7, 7, 17, 43, 54),
        timestamp_local=datetime.datetime(2025, 7, 7, 19, 43, 54),
        device_id=3477316333,
        level='PRIME',
        feedback_long='PRIME_RT_HIGHEST_SS_AVAILABLE_ACWR_POS',
        feedback_short='READY_FOR_ACTION',
        score=100,
        sleep_score=80,
        sleep_score_factor_percent=70,
        sleep_score_factor_feedback='GOOD',
        recovery_time=1.0,
        recovery_time_factor_percent=99,
        recovery_time_factor_feedback='GOOD',
        acwr_factor_percent=100,
        acwr_factor_feedback='VERY_GOOD',
        acute_load=20,
        stress_history_factor_percent=72,
        stress_history_factor_feedback='GOOD',
        hrv_factor_percent=92,
        hrv_factor_feedback='GOOD',
        hrv_weekly_average=53,
        sleep_history_factor_percent=92,
        sleep_history_factor_feedback='VERY_GOOD',
        valid_sleep=True,
        input_context='AFTER_POST_EXERCISE_RESET',
        primary_activity_tracker=True,
        recovery_time_change_phrase='REACHED_ZERO'
    )
]
```

### Filter by input context

```python
entries = garth.TrainingReadinessData.get("2025-07-07")
morning = next(e for e in entries if e.input_context == "AFTER_WAKEUP_RESET")
post_exercise = [e for e in entries if e.input_context == "AFTER_POST_EXERCISE_RESET"]
```
