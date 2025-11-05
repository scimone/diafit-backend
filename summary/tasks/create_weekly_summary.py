# summary/tasks/create_weekly_summary.py

from datetime import date, timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

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
            cgm_coverage=Avg("cgm_coverage"),
            total_bolus=Avg("total_bolus"),
            total_meals=Avg("total_meals"),
            total_carbs=Avg("total_carbs"),
            total_proteins=Avg("total_proteins"),
            total_fats=Avg("total_fats"),
            total_calories=Avg("total_calories"),
        )

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
                "cgm_coverage": round(aggregated["cgm_coverage"] or 0),
                "total_bolus": aggregated["total_bolus"] or 0,
                "total_meals": aggregated["total_meals"] or 0,
                "total_carbs": aggregated["total_carbs"] or 0,
                "total_proteins": aggregated["total_proteins"] or 0,
                "total_fats": aggregated["total_fats"] or 0,
                "total_calories": aggregated["total_calories"] or 0,
            },
        )

        print(
            f"✅ Weekly summary for {user.username} ({target_year}-W{target_week:02d}) created/updated."
        )

    print("🏁 Weekly summary task completed.")
