# User

User profile, settings, and daily summary data.

## Daily Summary

Get a comprehensive daily summary including calories, steps, heart rate,
stress, body battery, and more.

!!! tip "Date defaults to today"
    `.get()` and `.list()` accept an optional date parameter that defaults to
    today if not provided:
    ```python
    garth.DailySummary.get()  # Get today's summary
    ```

### Get single day

```python
garth.DailySummary.get("2025-06-14")
```

```python
DailySummary(
    user_profile_id=131234790,
    calendar_date=datetime.date(2025, 6, 14),
    total_kilocalories=2252,
    active_kilocalories=99,
    total_steps=5459,
    total_distance_meters=4471,
    min_heart_rate=49,
    max_heart_rate=104,
    min_avg_heart_rate=50,
    max_avg_heart_rate=101,
    resting_heart_rate=51,
    last_seven_days_avg_resting_heart_rate=50,
    max_stress_level=99,
    average_stress_level=24,
    stress_qualifier='BALANCED',
    body_battery_at_wake_time=92,
    body_battery_highest_value=92,
    body_battery_lowest_value=32,
    moderate_intensity_minutes=0,
    vigorous_intensity_minutes=0,
    active_seconds=3828,
    highly_active_seconds=345,
    sedentary_seconds=53385,
    sleeping_seconds=28842,
    floors_ascended=4.31299,
    floors_descended=8.86286,
    average_spo_2=None,
    lowest_spo_2=None,
    avg_waking_respiration_value=14,
    highest_respiration_value=23,
    lowest_respiration_value=6
)
```

### Get date range

```python
garth.DailySummary.list("2025-06-14", 2)
```

```python
[
    DailySummary(
        user_profile_id=131234790,
        calendar_date=datetime.date(2025, 6, 14),
        total_kilocalories=2252,
        active_kilocalories=99,
        total_steps=5459,
        total_distance_meters=4471,
        min_heart_rate=49,
        max_heart_rate=104,
        min_avg_heart_rate=50,
        max_avg_heart_rate=101,
        resting_heart_rate=51,
        last_seven_days_avg_resting_heart_rate=50,
        max_stress_level=99,
        average_stress_level=24,
        stress_qualifier='BALANCED',
        body_battery_at_wake_time=92,
        body_battery_highest_value=92,
        body_battery_lowest_value=32,
        moderate_intensity_minutes=0,
        vigorous_intensity_minutes=0,
        active_seconds=3828,
        highly_active_seconds=345,
        sedentary_seconds=53385,
        sleeping_seconds=28842,
        floors_ascended=4.31299,
        floors_descended=8.86286,
        average_spo_2=None,
        lowest_spo_2=None,
        avg_waking_respiration_value=14,
        highest_respiration_value=23,
        lowest_respiration_value=6
    ),
    DailySummary(
        user_profile_id=131234790,
        calendar_date=datetime.date(2025, 6, 13),
        total_kilocalories=2484,
        active_kilocalories=331,
        total_steps=11400,
        total_distance_meters=9726,
        min_heart_rate=46,
        max_heart_rate=130,
        min_avg_heart_rate=47,
        max_avg_heart_rate=127,
        resting_heart_rate=49,
        last_seven_days_avg_resting_heart_rate=49,
        max_stress_level=90,
        average_stress_level=23,
        stress_qualifier='BALANCED',
        body_battery_at_wake_time=100,
        body_battery_highest_value=100,
        body_battery_lowest_value=27,
        moderate_intensity_minutes=30,
        vigorous_intensity_minutes=2,
        active_seconds=6478,
        highly_active_seconds=2203,
        sedentary_seconds=48657,
        sleeping_seconds=29062,
        floors_ascended=23.72441,
        floors_descended=23.06759,
        average_spo_2=None,
        lowest_spo_2=None,
        avg_waking_respiration_value=15,
        highest_respiration_value=23,
        lowest_respiration_value=7
    )
]
```

## User Profile

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
    location="Ciudad de M\u00e9xico, CDMX",
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
        # ... more roles
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

## User Settings

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
