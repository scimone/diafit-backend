# summary/tasks/create_weekly_summary.py

from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

from summary.models import DailySummary, WeeklySummary
from summary.util.calculate_agp import calculate_agp_from_cgm, calculate_agp_summary


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

        # Calculate AGP from CGM data for the week
        start_datetime = datetime.combine(
            week_start, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        end_datetime = datetime.combine(
            week_end, datetime.max.time(), tzinfo=dt_timezone.utc
        )
        cgm_data = user.cgmentity_set.filter(
            timestamp__range=(start_datetime, end_datetime)
        )
        agp_data = calculate_agp_from_cgm(cgm_data)
        agp_summary_data = calculate_agp_summary(agp_data) if agp_data else None

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
            },
        )

        print(
            f"✅ Weekly summary for {user.username} ({target_year}-W{target_week:02d}) created/updated."
        )

    print("🏁 Weekly summary task completed.")
