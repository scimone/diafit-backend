# summary/tasks/create_weekly_summary.py

from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional

import pytz
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

from diafit_backend.models.sleep_entity import SleepSessionEntity, SleepType
from summary.features.agp import (
    TIME_PERIODS,
    calculate_agp_from_cgm,
    calculate_agp_summary,
    detect_agp_patterns,
)
from summary.models import DailySummary, WeeklySummary


def create_weekly_summary(
    target_year: Optional[int] = None,
    target_week: Optional[int] = None,
):
    """
    Create weekly summary for all users by aggregating daily summaries.

    Args:
        target_year (int, optional): Year to summarize (defaults to last week)
        target_week (int, optional): Week number to summarize (defaults to last week)
    """

    User = get_user_model()
    now = timezone.now()

    # Determine target week
    if not target_year or not target_week:
        # Get last complete week
        last_monday = now.date() - timedelta(days=now.weekday() + 7)
        target_year, target_week, _ = last_monday.isocalendar()

    # Calculate date range for the week
    jan_4 = date(target_year, 1, 4)
    week_start = jan_4 + timedelta(days=(target_week - 1) * 7 - jan_4.weekday())
    week_end = week_start + timedelta(days=6)

    print(
        f"📅 Generating weekly summary for {target_year}-W{target_week:02d} ({week_start} to {week_end})"
    )

    for user in User.objects.all():
        # Get daily summaries for this week
        daily_summaries = DailySummary.objects.filter(
            user=user, date__range=(week_start, week_end)
        )

        if not daily_summaries.exists():
            continue

        # Aggregate the daily summaries
        aggregated = daily_summaries.aggregate(
            glucose_avg=Avg("glucose_avg"),
            glucose_std=Avg("glucose_std"),
            time_in_range=Avg("time_in_range"),
            time_below_range=Avg("time_below_range"),
            time_above_range=Avg("time_above_range"),
            daily_cgm_coverage=Avg("daily_cgm_coverage"),
            daily_total_bolus=Avg("daily_total_bolus"),  # Average per day
            daily_total_meals=Avg("daily_total_meals"),  # Average per day
            daily_total_carbs=Avg("daily_total_carbs"),  # Average per day
            daily_total_proteins=Avg("daily_total_proteins"),  # Average per day
            daily_total_fats=Avg("daily_total_fats"),  # Average per day
            daily_total_calories=Avg("daily_total_calories"),  # Average per day
        )

        # Calculate sleep metrics from sleep sessions for the week
        start_datetime = datetime.combine(
            week_start, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        end_datetime = datetime.combine(
            week_end, datetime.max.time(), tzinfo=dt_timezone.utc
        )

        sleep_sessions = SleepSessionEntity.objects.filter(
            user=user,
            type=SleepType.SLEEP,
            start_time__range=(start_datetime, end_datetime),
        )

        daily_sleep_duration = None
        daily_deep_sleep_duration = None
        daily_rem_sleep_duration = None
        avg_fall_asleep_time = None
        avg_wake_up_time = None

        if sleep_sessions.exists():
            # Calculate average sleep durations per session (in minutes)
            session_count = sleep_sessions.count()
            total_sleep = sum(s.total_duration_minutes or 0 for s in sleep_sessions)
            daily_sleep_duration = (
                total_sleep / session_count
            )  # Average minutes per session

            total_deep = sum(s.deep_sleep_minutes or 0 for s in sleep_sessions)
            daily_deep_sleep_duration = total_deep / session_count

            total_rem = sum(s.rem_sleep_minutes or 0 for s in sleep_sessions)
            daily_rem_sleep_duration = (
                total_rem / session_count
            )  # Calculate average fall asleep and wake up times (convert to user's local timezone)
            user_tz = pytz.timezone(
                user.timezone
                if hasattr(user, "timezone") and user.timezone
                else "Europe/Berlin"
            )

            fall_asleep_times = [
                s.start_time.astimezone(user_tz).time() for s in sleep_sessions
            ]
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
                from datetime import time

                avg_fall_asleep_time = time(
                    hour=avg_minutes // 60, minute=avg_minutes % 60
                )

            wake_up_times = [
                s.end_time.astimezone(user_tz).time() for s in sleep_sessions
            ]
            if wake_up_times:
                total_minutes = sum(t.hour * 60 + t.minute for t in wake_up_times)
                avg_minutes = total_minutes // len(wake_up_times)
                from datetime import time

                avg_wake_up_time = time(hour=avg_minutes // 60, minute=avg_minutes % 60)

        # Calculate AGP from CGM data for the week
        cgm_data = user.cgmentity_set.filter(
            timestamp__range=(start_datetime, end_datetime)
        )
        agp_data = calculate_agp_from_cgm(cgm_data)
        agp_summary_data = (
            calculate_agp_summary(agp_data, TIME_PERIODS) if agp_data else None
        )
        agp_patterns = detect_agp_patterns(agp_data) if agp_data else None

        WeeklySummary.objects.update_or_create(
            user=user,
            year=target_year,
            week=target_week,
            defaults={
                "glucose_avg": round(aggregated["glucose_avg"] or 0),
                "glucose_std": round(aggregated["glucose_std"] or 0),
                "time_in_range": round(aggregated["time_in_range"] or 0),
                "time_below_range": round(aggregated["time_below_range"] or 0),
                "time_above_range": round(aggregated["time_above_range"] or 0),
                "daily_cgm_coverage": round(aggregated["daily_cgm_coverage"] or 0),
                "daily_total_bolus": aggregated["daily_total_bolus"] or 0,
                "daily_total_meals": aggregated["daily_total_meals"] or 0,
                "daily_total_carbs": aggregated["daily_total_carbs"] or 0,
                "daily_total_proteins": aggregated["daily_total_proteins"] or 0,
                "daily_total_fats": aggregated["daily_total_fats"] or 0,
                "daily_total_calories": aggregated["daily_total_calories"] or 0,
                "agp": agp_data,
                "agp_summary": agp_summary_data,
                "agp_trends": agp_patterns,
                "daily_sleep_duration": daily_sleep_duration,
                "daily_deep_sleep_duration": daily_deep_sleep_duration,
                "daily_rem_sleep_duration": daily_rem_sleep_duration,
                "avg_fall_asleep_time": avg_fall_asleep_time,
                "avg_wake_up_time": avg_wake_up_time,
            },
        )

        print(
            f"✅ Weekly summary for {user.username} ({target_year}-W{target_week:02d}) created/updated."
        )

    print("🏁 Weekly summary task completed.")
