# summary/features/statistics/bolus_stats.py

from typing import Dict, Optional

from django.db.models import QuerySet, Sum


def calculate_bolus_stats(
    bolus_queryset: QuerySet, period_days: int = 1
) -> Optional[Dict]:
    """
    Calculate bolus statistics.

    Args:
        bolus_queryset: QuerySet of bolus entities
        period_days: Number of days in the period (for averaging)

    Returns:
        Dict with total_bolus and avg_bolus_per_day
    """
    total_bolus = bolus_queryset.aggregate(total=Sum("value"))["total"] or 0
    avg_bolus_per_day = total_bolus / period_days if period_days > 0 else total_bolus

    return {
        "total_bolus": total_bolus,
        "avg_bolus_per_day": avg_bolus_per_day,
    }
