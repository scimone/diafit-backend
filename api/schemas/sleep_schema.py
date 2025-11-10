from datetime import datetime
from typing import List, Optional

from ninja import Schema


class SleepStageInSchema(Schema):
    """Schema for creating a sleep stage entry."""

    start_time: datetime
    end_time: datetime
    stage: int
    duration_minutes: Optional[int] = None


class SleepStageOutSchema(Schema):
    """Schema for sleep stage output."""

    id: int
    session_id: int
    start_time: datetime
    end_time: datetime
    stage: int
    duration_minutes: Optional[int]


class SleepSessionInSchema(Schema):
    """Schema for creating a sleep session entry."""

    user_id: int
    start_time: datetime
    end_time: datetime
    source: str = "Unknown"
    source_id: Optional[str] = None
    total_duration_minutes: Optional[int] = None
    deep_sleep_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    stages: Optional[List[SleepStageInSchema]] = None


class SleepSessionOutSchema(Schema):
    """Schema for sleep session output."""

    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    type: str
    source: str
    source_id: Optional[str]
    total_duration_minutes: Optional[int]
    deep_sleep_minutes: Optional[int]
    light_sleep_minutes: Optional[int]
    rem_sleep_minutes: Optional[int]
    awake_minutes: Optional[int]
    stages: Optional[List[SleepStageOutSchema]] = None
