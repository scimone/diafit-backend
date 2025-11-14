# summary/features/statistics/sleep_stats.py

from datetime import time
from typing import Dict, Optional

import pytz
from django.db.models import QuerySet


def calculate_sleep_stats(
    sleep_sessions_queryset: QuerySet, user_timezone: str = "Europe/Berlin"
) -> Optional[Dict]:
    """
    Calculate sleep statistics from sleep sessions.

    Args:
        sleep_sessions_queryset: QuerySet of SleepSessionEntity objects
        user_timezone: User's timezone for time calculations

    Returns:
        Dict with sleep duration metrics and average sleep/wake times
        or None if no data
    """
    if not sleep_sessions_queryset.exists():
        return None

    session_count = sleep_sessions_queryset.count()

    # Calculate average sleep durations per session (in minutes)
    total_sleep = sum(s.total_duration_minutes or 0 for s in sleep_sessions_queryset)
    daily_sleep_duration = total_sleep / session_count

    total_deep = sum(s.deep_sleep_minutes or 0 for s in sleep_sessions_queryset)
    daily_deep_sleep_duration = total_deep / session_count

    total_rem = sum(s.rem_sleep_minutes or 0 for s in sleep_sessions_queryset)
    daily_rem_sleep_duration = total_rem / session_count

    # Calculate average fall asleep and wake up times
    user_tz = pytz.timezone(user_timezone)

    fall_asleep_times = [
        s.start_time.astimezone(user_tz).time() for s in sleep_sessions_queryset
    ]
    avg_fall_asleep_time = None
    if fall_asleep_times:
        # Handle circular time (bedtime typically 20:00-03:00)
        minutes = []
        for t in fall_asleep_times:
            mins = t.hour * 60 + t.minute
            if mins < 720:  # Before 12:00 - treat as next day
                mins += 1440
            minutes.append(mins)
        avg_minutes = sum(minutes) // len(minutes)
        avg_minutes = avg_minutes % 1440  # Wrap back to 24-hour format
        avg_fall_asleep_time = time(hour=avg_minutes // 60, minute=avg_minutes % 60)

    wake_up_times = [
        s.end_time.astimezone(user_tz).time() for s in sleep_sessions_queryset
    ]
    avg_wake_up_time = None
    if wake_up_times:
        total_minutes = sum(t.hour * 60 + t.minute for t in wake_up_times)
        avg_minutes = total_minutes // len(wake_up_times)
        avg_wake_up_time = time(hour=avg_minutes // 60, minute=avg_minutes % 60)

    return {
        "daily_sleep_duration": daily_sleep_duration,
        "daily_deep_sleep_duration": daily_deep_sleep_duration,
        "daily_rem_sleep_duration": daily_rem_sleep_duration,
        "avg_fall_asleep_time": avg_fall_asleep_time,
        "avg_wake_up_time": avg_wake_up_time,
    }
