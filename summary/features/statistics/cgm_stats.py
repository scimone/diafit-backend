# summary/features/statistics/cgm_stats.py

from datetime import datetime
from statistics import median
from typing import Dict, Optional

from django.db.models import Avg, QuerySet, StdDev


def calculate_cgm_stats(cgm_queryset: QuerySet) -> Optional[Dict]:
    """
    Calculate glucose statistics from CGM data.

    Args:
        cgm_queryset: QuerySet of CGM entities

    Returns:
        Dict with glucose_avg, glucose_std, time_in_range, time_below_range, time_above_range
        or None if no data
    """
    if not cgm_queryset.exists():
        return None

    glucose_avg = cgm_queryset.aggregate(avg=Avg("value_mgdl"))["avg"] or 0
    glucose_std = cgm_queryset.aggregate(std=StdDev("value_mgdl"))["std"] or 0

    total = cgm_queryset.count() or 1
    tir = cgm_queryset.filter(value_mgdl__range=(70, 180)).count() / total * 100
    tbr = cgm_queryset.filter(value_mgdl__lt=70).count() / total * 100
    tar = cgm_queryset.filter(value_mgdl__gt=180).count() / total * 100

    return {
        "glucose_avg": round(glucose_avg),
        "glucose_std": round(glucose_std),
        "time_in_range": round(tir),
        "time_below_range": round(tbr),
        "time_above_range": round(tar),
    }


def calculate_cgm_coverage(
    cgm_queryset: QuerySet,
    start: datetime,
    end: datetime,
    expected_interval_seconds: Optional[float] = None,
    fallback_interval_seconds: float = 300.0,  # default 5 minutes
) -> float:
    """
    Calculate CGM coverage percentage for a time period.

    Each reading covers up to half the distance to previous and half to next,
    but each half is capped by expected_interval_seconds/2. Edge readings use
    the distance to start/end.

    Args:
        cgm_queryset: QuerySet of CGM entities
        start: Start of time period
        end: End of time period
        expected_interval_seconds: Optional known sampling interval. If None, inferred as median delta.
        fallback_interval_seconds: Default interval if no inference possible (default: 5 minutes)

    Returns:
        Coverage percentage (0-100)
    """
    timestamps = list(cgm_queryset.values_list("timestamp", flat=True))

    if not timestamps:
        return 0.0

    # ensure sorted
    timestamps = sorted(timestamps)

    # total window seconds
    total_seconds = (end - start).total_seconds()
    if total_seconds <= 0:
        return 0.0

    # compute deltas (in seconds) between consecutive timestamps
    deltas = []
    for i in range(len(timestamps) - 1):
        d = (timestamps[i + 1] - timestamps[i]).total_seconds()
        if d > 0:
            deltas.append(d)

    # infer expected interval if not provided
    if expected_interval_seconds is None:
        if deltas:
            expected_interval_seconds = float(median(deltas))
        else:
            expected_interval_seconds = fallback_interval_seconds

    # guard: must be > 0
    expected_interval_seconds = max(float(expected_interval_seconds), 1.0)

    half_expected = expected_interval_seconds / 2.0

    covered_seconds = 0.0
    n = len(timestamps)

    for i, ts in enumerate(timestamps):
        # left coverage
        if i == 0:
            left_gap = (ts - start).total_seconds()
            left_covered = min(left_gap, half_expected)
        else:
            prev_gap = (ts - timestamps[i - 1]).total_seconds()
            left_covered = min(prev_gap / 2.0, half_expected)

        # right coverage
        if i == n - 1:
            right_gap = (end - ts).total_seconds()
            right_covered = min(right_gap, half_expected)
        else:
            next_gap = (timestamps[i + 1] - ts).total_seconds()
            right_covered = min(next_gap / 2.0, half_expected)

        covered_seconds += max(0.0, left_covered) + max(0.0, right_covered)

    # covered_seconds may slightly exceed total_seconds due to rounding -> cap
    covered_seconds = min(covered_seconds, total_seconds)

    coverage_percent = (covered_seconds / total_seconds) * 100.0
    return round(coverage_percent)
