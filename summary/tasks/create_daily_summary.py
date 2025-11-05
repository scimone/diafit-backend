# summary/tasks/create_daily_summary.py

from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, StdDev, Sum
from django.utils import timezone
from summary.utils.compute_cgm_coverage import compute_cgm_coverage

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

        glucose_avg = cgm_qs.aggregate(avg=Avg("value_mgdl"))["avg"] or 0
        glucose_std = cgm_qs.aggregate(std=StdDev("value_mgdl"))["std"] or 0

        total = cgm_qs.count() or 1
        tir = cgm_qs.filter(value_mgdl__range=(70, 180)).count() / total * 100
        tbr = cgm_qs.filter(value_mgdl__lt=70).count() / total * 100
        tar = cgm_qs.filter(value_mgdl__gt=180).count() / total * 100

        # --- CGM coverage ---
        timestamps = list(cgm_qs.values_list("timestamp", flat=True))
        cgm_coverage = compute_cgm_coverage(timestamps, start, end)

        # --- Bolus stats ---
        bolus_qs = user.bolusentity_set.filter(timestamp_utc__range=(start, end))
        total_bolus = bolus_qs.aggregate(total=Sum("value"))["total"] or 0

        # --- Meal stats ---
        meal_qs = user.mealentity_set.filter(meal_time_utc__range=(start, end))
        totals = meal_qs.aggregate(
            carbs=Sum("carbohydrates"),
            proteins=Sum("proteins"),
            fats=Sum("fats"),
            calories=Sum("calories"),
            count=Count("id"),
        )

        total_carbs = totals["carbs"] or 0
        total_proteins = totals["proteins"] or 0
        total_fats = totals["fats"] or 0
        total_calories = totals["calories"] or 0
        total_meals = totals["count"] or 0

        DailySummary.objects.update_or_create(
            user=user,
            date=summary_date,
            defaults={
                "glucose_avg": round(glucose_avg),
                "glucose_std": round(glucose_std),
                "time_in_range": round(tir),
                "time_below_range": round(tbr),
                "time_above_range": round(tar),
                "cgm_coverage": round(cgm_coverage),
                "total_bolus": total_bolus,
                "total_meals": total_meals,
                "total_carbs": total_carbs,
                "total_proteins": total_proteins,
                "total_fats": total_fats,
                "total_calories": total_calories,
            },
        )

        print(f"✅ Summary for {user.username} ({summary_date}) created/updated.")
    print("🏁 Daily summary task completed.")
