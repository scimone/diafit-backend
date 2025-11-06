import numpy as np


def detect_agp_patterns(percentiles: dict):
    """
    Extract notable patterns from AGP percentile data.
    Input: percentiles dict with keys p10, p25, p50, p75, p90, time (288 points)
    Returns: list of short human-readable pattern strings
    """
    p10, p25, p50, p75, p90 = map(
        np.array,
        [
            percentiles["p10"],
            percentiles["p25"],
            percentiles["p50"],
            percentiles["p75"],
            percentiles["p90"],
        ],
    )

    times = percentiles["time"]
    patterns = []

    # Basic metrics
    spread = p90 - p10
    slope = np.gradient(p50)

    # Divide the day roughly into chunks (72 = 6h)
    sections = {
        "night": slice(0, 72),
        "morning": slice(72, 144),
        "afternoon": slice(144, 216),
        "evening": slice(216, 288),
    }

    # Pattern detection thresholds (tunable)
    HIGH_VARIABILITY = 60  # mg/dL p90–p10
    STRONG_RISE = 0.6  # mg/dL/min
    STRONG_DROP = -0.5  # mg/dL/min

    # --- 1. Variability patterns ---
    for name, rng in sections.items():
        avg_spread = np.mean(spread[rng])
        if avg_spread > HIGH_VARIABILITY:
            patterns.append(f"High variability during {name} period.")

    # --- 2. Rising/falling trends ---
    if np.mean(slope[72:120]) > STRONG_RISE:
        patterns.append("Rapid glucose rise after breakfast (morning spike).")
    if np.mean(slope[216:264]) > STRONG_RISE:
        patterns.append("Evening glucose rise, possibly after dinner.")
    if np.mean(slope[0:48]) < STRONG_DROP:
        patterns.append("Overnight glucose drop trend.")

    # --- 3. Level patterns ---
    if np.mean(p50[0:72]) < 100:
        patterns.append("Stable overnight glucose in target range.")
    if np.mean(p50[72:144]) > 140:
        patterns.append("Elevated post-breakfast glucose levels.")
    if np.mean(p50[216:288]) > 150:
        patterns.append("High average glucose in the evening.")

    # Deduplicate similar patterns
    return sorted(set(patterns))
