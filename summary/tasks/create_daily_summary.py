# summary/tasks/create_daily_summary.py

from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from summary.features.statistics import (
    calculate_bolus_stats,
    calculate_cgm_coverage,
    calculate_cgm_stats,
    calculate_meal_stats,
)
from summary.models import DailySummary


def create_daily_summary(
    target_date: Optional[date] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    mode: str = "auto",  # "auto" | "manual" | "partial"
):
    """
    Create daily summary for all users within a given time window.

    Args:
        target_date (date, optional): date to summarize (used if no start/end given)
        start (datetime, optional): start of window (inclusive)
        end (datetime, optional): end of window (exclusive)
        mode (str): optional label for debugging/logging ("auto", "manual", "partial")

    Behavior:
        - If no start/end → defaults to yesterday's full day (00:00–00:00 next day)
        - If only end is provided → assumes start is that day's midnight
        - If end > now → clipped to current time
        - Safe for partial summaries (e.g., up to 16:20 today)
    """

    User = get_user_model()
    now = timezone.now()

    # Determine date and window
    if not start or not end:
        summary_date = target_date or (now.date() - timedelta(days=1))
        start = datetime.combine(
            summary_date, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        end = start + timedelta(days=1)
    else:
        summary_date = start.date()

    # Clip future times
    if end > now:
        end = now

    print(f"📆 Generating summary for {summary_date} ({start} → {end}) [{mode}]")

    for user in User.objects.all():
        # --- CGM stats ---
        cgm_qs = user.cgmentity_set.filter(timestamp__range=(start, end)).order_by(
            "timestamp"
        )
        if not cgm_qs.exists():
            continue

        cgm_stats = calculate_cgm_stats(cgm_qs)
        if not cgm_stats:
            continue

        cgm_coverage = calculate_cgm_coverage(cgm_qs, start, end)

        # --- Bolus stats ---
        bolus_qs = user.bolusentity_set.filter(timestamp_utc__range=(start, end))
        bolus_stats = calculate_bolus_stats(bolus_qs, period_days=1)

        # --- Meal stats ---
        meal_qs = user.mealentity_set.filter(meal_time_utc__range=(start, end))
        meal_stats = calculate_meal_stats(meal_qs, period_days=1)

        DailySummary.objects.update_or_create(
            user=user,
            date=summary_date,
            defaults={
                "glucose_avg": cgm_stats["glucose_avg"],
                "glucose_std": cgm_stats["glucose_std"],
                "time_in_range": cgm_stats["time_in_range"],
                "time_below_range": cgm_stats["time_below_range"],
                "time_above_range": cgm_stats["time_above_range"],
                "daily_cgm_coverage": round(cgm_coverage),
                "daily_total_bolus": bolus_stats["total_bolus"],
                "daily_total_meals": meal_stats["total_meals"],
                "daily_total_carbs": meal_stats["total_carbs"],
                "daily_total_proteins": meal_stats["total_proteins"],
                "daily_total_fats": meal_stats["total_fats"],
                "daily_total_calories": meal_stats["total_calories"],
            },
        )

        print(f"✅ Summary for {user.username} ({summary_date}) created/updated.")
    print("🏁 Daily summary task completed.")
