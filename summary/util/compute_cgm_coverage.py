# summary/util/compute_cgm_coverage.py

from datetime import datetime
from statistics import median
from typing import List, Optional


def compute_cgm_coverage(
    timestamps: List[datetime],
    start: datetime,
    end: datetime,
    expected_interval_seconds: Optional[float] = None,
    fallback_interval_seconds: float = 300.0,  # default 5 minutes if no inference possible
) -> float:
    """
    Compute CGM coverage as percent of [start, end) covered by readings given by `timestamps`.

    - timestamps: list of timezone-aware datetimes (sorted or unsorted)
    - start, end: timezone-aware datetimes delimiting the day/window
    - expected_interval_seconds: optional known sampling interval in seconds. If None, inferred as median delta.
    - Returns coverage_percent (0.0 - 100.0)

    Approach:
      Each reading covers up to half the distance to previous and half to next,
      but each half is capped by expected_interval_seconds/2. Edge readings use the distance to start/end.
    """

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
