# summary/tasks/create_rolling_summary.py

from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, StdDev, Sum
from django.utils import timezone

from summary.models import DailySummary, RollingSummary


def create_rolling_summary(
    period_days_list: Optional[List[int]] = None,
    end_date: Optional[datetime] = None,
):
    """
    Create rolling summaries for all users.
    For periods <= 3 days: Uses raw CGM, bolus, and meal data
    For periods > 3 days: Uses aggregated daily summaries
    This overwrites existing rolling summaries for the specified periods.

    Args:
        period_days_list (List[int], optional): List of rolling periods in days
                                               (defaults to [1, 3, 7, 14, 30, 90])
        end_date (datetime, optional): End date for rolling periods (defaults to now)
    """

    User = get_user_model()
    now = timezone.now()

    if period_days_list is None:
        period_days_list = [1, 3, 7, 14, 30, 90]

    if end_date is None:
        end_date = now

    # Convert to date for consistency with daily summaries
    end_date_only = end_date.date()

    print(
        f"📊 Generating rolling summaries for periods {period_days_list} ending {end_date_only}"
    )

    for user in User.objects.all():
        for period_days in period_days_list:
            start_date = end_date_only - timedelta(days=period_days - 1)

            if period_days <= 3:
                # Use raw data for short periods (1-3 days)
                start_datetime = datetime.combine(
                    start_date, datetime.min.time(), tzinfo=dt_timezone.utc
                )
                end_datetime = datetime.combine(
                    end_date_only, datetime.max.time(), tzinfo=dt_timezone.utc
                )

                # Clip to current time if end is in the future
                if end_datetime > now:
                    end_datetime = now

                # --- CGM stats ---
                cgm_qs = user.cgmentity_set.filter(
                    timestamp__range=(start_datetime, end_datetime)
                )
                if not cgm_qs.exists():
                    print(
                        f"⚠️  No CGM data found for {user.username} from {start_datetime} to {end_datetime} (period: {period_days}d)"
                    )
                    continue

                glucose_avg = cgm_qs.aggregate(avg=Avg("value_mgdl"))["avg"] or 0
                glucose_std = cgm_qs.aggregate(std=StdDev("value_mgdl"))["std"] or 0

                total = cgm_qs.count() or 1
                tir = cgm_qs.filter(value_mgdl__range=(70, 180)).count() / total * 100
                tbr = cgm_qs.filter(value_mgdl__lt=70).count() / total * 100
                tar = cgm_qs.filter(value_mgdl__gt=180).count() / total * 100

                # --- CGM coverage (simplified for now, can be improved later) ---
                total_minutes = (end_datetime - start_datetime).total_seconds() / 60
                expected_readings = total_minutes / 5  # Assuming 5-minute intervals
                cgm_coverage = (
                    min(100, (cgm_qs.count() / expected_readings) * 100)
                    if expected_readings > 0
                    else 0
                )

                # --- Bolus stats ---
                bolus_qs = user.bolusentity_set.filter(
                    timestamp_utc__range=(start_datetime, end_datetime)
                )
                total_bolus_sum = bolus_qs.aggregate(total=Sum("value"))["total"] or 0
                avg_bolus_per_day = total_bolus_sum / period_days

                # --- Meal stats ---
                meal_qs = user.mealentity_set.filter(
                    meal_time_utc__range=(start_datetime, end_datetime)
                )
                totals = meal_qs.aggregate(
                    carbs=Sum("carbohydrates"),
                    proteins=Sum("proteins"),
                    fats=Sum("fats"),
                    calories=Sum("calories"),
                    count=Count("id"),
                )

                avg_carbs_per_day = (totals["carbs"] or 0) / period_days
                avg_proteins_per_day = (totals["proteins"] or 0) / period_days
                avg_fats_per_day = (totals["fats"] or 0) / period_days
                avg_calories_per_day = (totals["calories"] or 0) / period_days
                avg_meals_per_day = (totals["count"] or 0) / period_days

                # Create rolling summary with raw data
                RollingSummary.objects.update_or_create(
                    user=user,
                    period_days=period_days,
                    end_date=end_date_only,
                    defaults={
                        "start_date": start_date,
                        "glucose_avg": round(glucose_avg),
                        "glucose_std": round(glucose_std),
                        "time_in_range": round(tir),
                        "time_below_range": round(tbr),
                        "time_above_range": round(tar),
                        "daily_cgm_coverage": round(cgm_coverage),
                        "daily_total_bolus": round(avg_bolus_per_day, 2),
                        "daily_total_meals": round(avg_meals_per_day, 1),
                        "daily_total_carbs": round(avg_carbs_per_day, 1),
                        "daily_total_proteins": round(avg_proteins_per_day, 1),
                        "daily_total_fats": round(avg_fats_per_day, 1),
                        "daily_total_calories": round(avg_calories_per_day),
                        "agp": None,
                        "agp_summary": None,
                        "updated_at": now,
                    },
                )

            else:
                # Use aggregated daily summaries for longer periods (>3 days)
                daily_summaries = DailySummary.objects.filter(
                    user=user, date__range=(start_date, end_date_only)
                )

                if not daily_summaries.exists():
                    print(
                        f"⚠️  No daily summaries found for {user.username} from {start_date} to {end_date_only} (period: {period_days}d)"
                    )
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

                # Create rolling summary with aggregated data
                RollingSummary.objects.update_or_create(
                    user=user,
                    period_days=period_days,
                    end_date=end_date_only,
                    defaults={
                        "start_date": start_date,
                        "glucose_avg": round(aggregated["glucose_avg"] or 0),
                        "glucose_std": round(aggregated["glucose_std"] or 0),
                        "time_in_range": round(aggregated["time_in_range"] or 0),
                        "time_below_range": round(aggregated["time_below_range"] or 0),
                        "time_above_range": round(aggregated["time_above_range"] or 0),
                        "daily_cgm_coverage": round(
                            aggregated["daily_cgm_coverage"] or 0
                        ),
                        "daily_total_bolus": aggregated["daily_total_bolus"] or 0,
                        "daily_total_meals": aggregated["daily_total_meals"] or 0,
                        "daily_total_carbs": aggregated["daily_total_carbs"] or 0,
                        "daily_total_proteins": aggregated["daily_total_proteins"] or 0,
                        "daily_total_fats": aggregated["daily_total_fats"] or 0,
                        "daily_total_calories": aggregated["daily_total_calories"] or 0,
                        "agp": None,
                        "agp_summary": None,
                        "updated_at": now,
                    },
                )

            print(
                f"✅ Rolling {period_days}d summary for {user.username} ({start_date} to {end_date_only}) created/updated."
            )

    print("🏁 Rolling summary task completed.")
