# summary/tasks/create_quarterly_summary.py

from datetime import date, datetime
from datetime import timezone as dt_timezone
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

from summary.models import DailySummary, QuarterlySummary
from summary.util.calculate_agp import (
    calculate_agp_from_cgm,
    calculate_agp_summary,
    detect_agp_patterns,
)


def create_quarterly_summary(
    target_year: Optional[int] = None,
    target_quarter: Optional[int] = None,
):
    """
    Create quarterly summary for all users by aggregating daily summaries.

    Args:
        target_year (int, optional): Year to summarize (defaults to last quarter)
        target_quarter (int, optional): Quarter to summarize (1-4, defaults to last quarter)
    """

    User = get_user_model()
    now = timezone.now()

    # Determine target quarter
    if not target_year or not target_quarter:
        # Get last complete quarter
        current_quarter = (now.month - 1) // 3 + 1
        if current_quarter == 1:
            target_year = now.year - 1
            target_quarter = 4
        else:
            target_year = now.year
            target_quarter = current_quarter - 1

    # Calculate date range for the quarter
    quarter_start_months = {1: 1, 2: 4, 3: 7, 4: 10}
    start_month = quarter_start_months[target_quarter]
    end_month = start_month + 2

    quarter_start = date(target_year, start_month, 1)
    if end_month == 12:
        quarter_end = date(target_year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        quarter_end = date(target_year, end_month + 1, 1) - timezone.timedelta(days=1)

    print(
        f"📅 Generating quarterly summary for {target_year}-Q{target_quarter} ({quarter_start} to {quarter_end})"
    )

    for user in User.objects.all():
        # Get daily summaries for this quarter
        daily_summaries = DailySummary.objects.filter(
            user=user, date__range=(quarter_start, quarter_end)
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

        # Calculate AGP from CGM data for the quarter
        start_datetime = datetime.combine(
            quarter_start, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        end_datetime = datetime.combine(
            quarter_end, datetime.max.time(), tzinfo=dt_timezone.utc
        )
        cgm_data = user.cgmentity_set.filter(
            timestamp__range=(start_datetime, end_datetime)
        )
        agp_data = calculate_agp_from_cgm(cgm_data)
        agp_summary_data = calculate_agp_summary(agp_data) if agp_data else None
        agp_patterns = detect_agp_patterns(agp_data) if agp_data else None

        QuarterlySummary.objects.update_or_create(
            user=user,
            year=target_year,
            quarter=target_quarter,
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
            },
        )

        print(
            f"✅ Quarterly summary for {user.username} ({target_year}-Q{target_quarter}) created/updated."
        )

    print("🏁 Quarterly summary task completed.")
