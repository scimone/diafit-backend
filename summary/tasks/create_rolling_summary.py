# summary/tasks/create_rolling_summary.py

import logging
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from typing import List, Optional

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
from summary.features.statistics import (
    calculate_bolus_stats,
    calculate_cgm_stats,
    calculate_meal_stats,
    calculate_sleep_stats,
)
from summary.models import DailySummary, RollingSummary

logger = logging.getLogger(__name__)


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

    # Ensure end_date is set to the start of the current day for consistency
    if end_date is None:
        end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Convert to date for consistency with daily summaries
    end_date_only = end_date.date()

    logger.info(
        f"📊 Generating rolling summaries for periods {period_days_list} ending {end_date_only}"
    )
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

                cgm_stats = calculate_cgm_stats(cgm_qs)
                if not cgm_stats:
                    continue

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
                bolus_stats = calculate_bolus_stats(bolus_qs, period_days)

                # --- Meal stats ---
                meal_qs = user.mealentity_set.filter(
                    meal_time_utc__range=(start_datetime, end_datetime)
                )
                meal_stats = calculate_meal_stats(meal_qs, period_days)

                # Calculate sleep metrics for short periods
                sleep_sessions = SleepSessionEntity.objects.filter(
                    user=user,
                    type=SleepType.SLEEP,
                    end_time__range=(start_datetime, end_datetime),
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
                avg_wake_up_time = (
                    sleep_stats["avg_wake_up_time"] if sleep_stats else None
                )

                # Calculate AGP for short periods
                try:
                    logger.info(
                        f"Calculating AGP for {user.username} ({period_days}d) with {cgm_qs.count()} CGM readings"
                    )
                    # Force queryset evaluation before passing to AGP functions
                    cgm_list = list(cgm_qs.values("timestamp", "value_mgdl"))
                    logger.info(f"CGM data retrieved: {len(cgm_list)} readings")

                    agp_data = calculate_agp_from_cgm(cgm_qs)
                    logger.info(
                        f"AGP data type: {type(agp_data)}, value: {agp_data is not None}"
                    )

                    agp_summary_data = (
                        calculate_agp_summary(agp_data, TIME_PERIODS)
                        if agp_data
                        else None
                    )
                    agp_patterns = detect_agp_patterns(agp_data) if agp_data else None

                    logger.info(
                        f"✅ AGP calculated for {user.username} ({period_days}d): data={bool(agp_data)}, summary={bool(agp_summary_data)}, patterns={bool(agp_patterns)}"
                    )
                    print(
                        f"  ℹ️  AGP calculated for {user.username} ({period_days}d): {bool(agp_data)}"
                    )
                except Exception as e:
                    logger.error(
                        f"⚠️  AGP calculation failed for {user.username} ({period_days}d): {e}",
                        exc_info=True,
                    )
                    print(
                        f"  ⚠️  AGP calculation failed for {user.username} ({period_days}d): {e}"
                    )
                    agp_data = None
                    agp_summary_data = None
                    agp_patterns = None

                # Create rolling summary with raw data
                RollingSummary.objects.update_or_create(
                    user=user,
                    period_days=period_days,
                    defaults={
                        "end_date": end_date_only,
                        "start_date": start_date,
                        "glucose_avg": cgm_stats["glucose_avg"],
                        "glucose_std": cgm_stats["glucose_std"],
                        "time_in_range": cgm_stats["time_in_range"],
                        "time_below_range": cgm_stats["time_below_range"],
                        "time_above_range": cgm_stats["time_above_range"],
                        "daily_cgm_coverage": round(cgm_coverage),
                        "daily_total_bolus": round(bolus_stats["avg_bolus_per_day"], 2),
                        "daily_total_meals": round(meal_stats["avg_meals_per_day"], 1),
                        "daily_total_carbs": round(meal_stats["avg_carbs_per_day"], 1),
                        "daily_total_proteins": round(
                            meal_stats["avg_proteins_per_day"], 1
                        ),
                        "daily_total_fats": round(meal_stats["avg_fats_per_day"], 1),
                        "daily_total_calories": round(
                            meal_stats["avg_calories_per_day"]
                        ),
                        "daily_sleep_duration": daily_sleep_duration,
                        "daily_deep_sleep_duration": daily_deep_sleep_duration,
                        "daily_rem_sleep_duration": daily_rem_sleep_duration,
                        "avg_fall_asleep_time": avg_fall_asleep_time,
                        "avg_wake_up_time": avg_wake_up_time,
                        "agp": agp_data,
                        "agp_summary": agp_summary_data,
                        "agp_trends": agp_patterns,
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

                # Calculate sleep metrics for longer periods
                start_datetime = datetime.combine(
                    start_date, datetime.min.time(), tzinfo=dt_timezone.utc
                )
                end_datetime = datetime.combine(
                    end_date_only, datetime.max.time(), tzinfo=dt_timezone.utc
                )
                if end_datetime > now:
                    end_datetime = now

                sleep_sessions = SleepSessionEntity.objects.filter(
                    user=user,
                    type=SleepType.SLEEP,
                    end_time__range=(start_datetime, end_datetime),
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
                avg_wake_up_time = (
                    sleep_stats["avg_wake_up_time"] if sleep_stats else None
                )

                # Calculate AGP from CGM data for longer periods
                try:
                    cgm_data = user.cgmentity_set.filter(
                        timestamp__range=(start_datetime, end_datetime)
                    )
                    cgm_count = cgm_data.count()
                    logger.info(
                        f"Calculating AGP for {user.username} ({period_days}d) with {cgm_count} CGM readings"
                    )
                    print(
                        f"  ℹ️  Calculating AGP for {user.username} ({period_days}d) with {cgm_count} CGM readings"
                    )

                    agp_data = calculate_agp_from_cgm(cgm_data)
                    agp_summary_data = (
                        calculate_agp_summary(agp_data, TIME_PERIODS)
                        if agp_data
                        else None
                    )
                    agp_patterns = detect_agp_patterns(agp_data) if agp_data else None

                    logger.info(
                        f"✅ AGP calculated for {user.username} ({period_days}d): data={bool(agp_data)}, summary={bool(agp_summary_data)}, patterns={bool(agp_patterns)}"
                    )
                    print(
                        f"  ℹ️  AGP calculated for {user.username} ({period_days}d): {bool(agp_data)}"
                    )
                except Exception as e:
                    logger.error(
                        f"⚠️  AGP calculation failed for {user.username} ({period_days}d): {e}",
                        exc_info=True,
                    )
                    print(
                        f"  ⚠️  AGP calculation failed for {user.username} ({period_days}d): {e}"
                    )
                    agp_data = None
                    agp_summary_data = None
                    agp_patterns = None

                # Create rolling summary with aggregated data
                RollingSummary.objects.update_or_create(
                    user=user,
                    period_days=period_days,
                    defaults={
                        "end_date": end_date_only,
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
                        "daily_sleep_duration": daily_sleep_duration,
                        "daily_deep_sleep_duration": daily_deep_sleep_duration,
                        "daily_rem_sleep_duration": daily_rem_sleep_duration,
                        "avg_fall_asleep_time": avg_fall_asleep_time,
                        "avg_wake_up_time": avg_wake_up_time,
                        "agp": agp_data,
                        "agp_summary": agp_summary_data,
                        "agp_trends": agp_patterns,
                        "updated_at": now,
                    },
                )

            print(
                f"✅ Rolling {period_days}d summary for {user.username} ({start_date} to {end_date_only}) created/updated."
            )

    logger.info("🏁 Rolling summary task completed.")
    print("🏁 Rolling summary task completed.")
