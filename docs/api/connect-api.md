# Connect API

The `garth.connectapi()` function allows you to make direct requests to the
Garmin Connect API and receive JSON responses.

## Making Requests

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

## Uploading Activities

```python
with open("12129115726_ACTIVITY.fit", "rb") as f:
    uploaded = garth.client.upload(f)
```

!!! note "FIT file requirements"
    Garmin doesn't accept uploads of _structured_ FIT files as outlined in
    [this conversation](https://github.com/matin/garth/issues/27). FIT files
    generated from workouts are accepted without issues.

### Response

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
