# summary/tasks/create_monthly_summary.py

from datetime import date, datetime
from datetime import timezone as dt_timezone
from typing import Optional

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
from summary.features.statistics import calculate_sleep_stats
from summary.models import DailySummary, MonthlySummary


def create_monthly_summary(
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
):
    """
    Create monthly summary for all users by aggregating daily summaries.

    Args:
        target_year (int, optional): Year to summarize (defaults to last month)
        target_month (int, optional): Month to summarize (defaults to last month)
    """

    User = get_user_model()
    now = timezone.now()

    # Determine target month
    if not target_year or not target_month:
        # Get last complete month
        if now.month == 1:
            target_year = now.year - 1
            target_month = 12
        else:
            target_year = now.year
            target_month = now.month - 1

    # Calculate date range for the month
    month_start = date(target_year, target_month, 1)
    if target_month == 12:
        month_end = date(target_year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        month_end = date(target_year, target_month + 1, 1) - timezone.timedelta(days=1)

    print(
        f"📅 Generating monthly summary for {target_year}-{target_month:02d} ({month_start} to {month_end})"
    )

    for user in User.objects.all():
        # Get daily summaries for this month
        daily_summaries = DailySummary.objects.filter(
            user=user, date__range=(month_start, month_end)
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

        # Calculate sleep metrics from sleep sessions for the month
        start_datetime = datetime.combine(
            month_start, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        end_datetime = datetime.combine(
            month_end, datetime.max.time(), tzinfo=dt_timezone.utc
        )

        sleep_sessions = SleepSessionEntity.objects.filter(
            user=user,
            type=SleepType.SLEEP,
            start_time__range=(start_datetime, end_datetime),
        )

        user_timezone = (
            user.timezone
            if hasattr(user, "timezone") and user.timezone
            else "Europe/Berlin"
        )
        sleep_stats = calculate_sleep_stats(sleep_sessions, user_timezone)

        daily_sleep_duration = (
            sleep_stats["daily_sleep_duration"] if sleep_stats else None
        )
        daily_deep_sleep_duration = (
            sleep_stats["daily_deep_sleep_duration"] if sleep_stats else None
        )
        daily_rem_sleep_duration = (
            sleep_stats["daily_rem_sleep_duration"] if sleep_stats else None
        )
        avg_fall_asleep_time = (
            sleep_stats["avg_fall_asleep_time"] if sleep_stats else None
        )
        avg_wake_up_time = sleep_stats["avg_wake_up_time"] if sleep_stats else None

        # Calculate AGP from CGM data for the month
        cgm_data = user.cgmentity_set.filter(
            timestamp__range=(start_datetime, end_datetime)
        )
        agp_data = calculate_agp_from_cgm(cgm_data)
        agp_summary_data = (
            calculate_agp_summary(agp_data, TIME_PERIODS) if agp_data else None
        )
        agp_patterns = detect_agp_patterns(agp_data) if agp_data else None

        MonthlySummary.objects.update_or_create(
            user=user,
            year=target_year,
            month=target_month,
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
            f"✅ Monthly summary for {user.username} ({target_year}-{target_month:02d}) created/updated."
        )

    print("🏁 Monthly summary task completed.")
