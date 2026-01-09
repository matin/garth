# Training Status

Training status data provides insights into your training load, fitness trends,
and acute:chronic workload ratio (ACWR).

## Daily Training Status

```python
garth.DailyTrainingStatus.list("2025-06-11", 1)
```

```python
[
    DailyTrainingStatus(
        calendar_date=datetime.date(2025, 6, 11),
        since_date=datetime.date(2025, 5, 31),
        weekly_training_load=None,
        training_status=7,
        timestamp=datetime.datetime(2025, 6, 11, 14, 31, 49),
        device_id=3469703076,
        load_tunnel_min=None,
        load_tunnel_max=None,
        load_level_trend=None,
        sport="RUNNING",
        sub_sport="GENERIC",
        fitness_trend_sport="RUNNING",
        fitness_trend=2,
        training_status_feedback_phrase="PRODUCTIVE_6",
        training_paused=False,
        primary_training_device=True,
        acwr_percent=57,
        acwr_status="OPTIMAL",
        acwr_status_feedback="FEEDBACK_3",
        daily_training_load_acute=399,
        max_training_load_chronic=450.0,
        min_training_load_chronic=240.0,
        daily_training_load_chronic=300,
        daily_acute_chronic_workload_ratio=1.3
    )
]
```

## Weekly Training Status

```python
garth.WeeklyTrainingStatus.list("2025-06-11", 4)
```

```python
[
    WeeklyTrainingStatus(
        calendar_date=datetime.date(2025, 5, 21),
        since_date=None,
        weekly_training_load=None,
        training_status=4,
        timestamp=datetime.datetime(2025, 5, 21, 10, 19, 30),
        device_id=3469703076,
        load_tunnel_min=None,
        load_tunnel_max=None,
        load_level_trend=None,
        sport="RUNNING",
        sub_sport="GENERIC",
        fitness_trend_sport="RUNNING",
        fitness_trend=2,
        training_status_feedback_phrase="MAINTAINING_2",
        training_paused=False,
        primary_training_device=True,
        acwr_percent=42,
        acwr_status="OPTIMAL",
        acwr_status_feedback="FEEDBACK_2",
        daily_training_load_acute=224,
        max_training_load_chronic=328.5,
        min_training_load_chronic=175.20000000000002,
        daily_training_load_chronic=219,
        daily_acute_chronic_workload_ratio=1.0
    ),
    # ... more entries
]
```

## Monthly Training Status

```python
garth.MonthlyTrainingStatus.list("2025-06-11", 6)
```

```python
[
    MonthlyTrainingStatus(
        calendar_date=datetime.date(2025, 1, 1),
        since_date=None,
        weekly_training_load=None,
        training_status=4,
        timestamp=datetime.datetime(2025, 1, 1, 5, 31, 56),
        device_id=3469703076,
        load_tunnel_min=None,
        load_tunnel_max=None,
        load_level_trend=None,
        sport="RUNNING",
        sub_sport="GENERIC",
        fitness_trend_sport="RUNNING",
        fitness_trend=2,
        training_status_feedback_phrase="MAINTAINING_3",
        training_paused=False,
        primary_training_device=True,
        acwr_percent=29,
        acwr_status="LOW",
        acwr_status_feedback="FEEDBACK_1",
        daily_training_load_acute=160,
        max_training_load_chronic=328.5,
        min_training_load_chronic=175.20000000000002,
        daily_training_load_chronic=219,
        daily_acute_chronic_workload_ratio=0.7
    ),
    # ... more entries
]
```
