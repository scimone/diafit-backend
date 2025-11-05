# summary/tasks/create_monthly_summary.py

from datetime import date
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

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
            },
        )

        print(
            f"✅ Monthly summary for {user.username} ({target_year}-{target_month:02d}) created/updated."
        )

    print("🏁 Monthly summary task completed.")
