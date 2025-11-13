"""
AGP Pattern Detection
Analyzes AGP data to detect notable glucose patterns and provide insights.
"""

import numpy as np

from . import config as cfg


def get_period_indices(start_hour, end_hour):
    """
    Get array indices for a time period, handling wraparound midnight.
    
    Args:
        start_hour: Starting hour (0-23)
        end_hour: Ending hour (0-24)
        
    Returns:
        np.array: Indices for the time period
    """
    if start_hour > end_hour:
        # Wraps around midnight (e.g., 22-7)
        indices1 = list(range(start_hour * cfg.POINTS_PER_HOUR, 24 * cfg.POINTS_PER_HOUR))
        indices2 = list(range(0, end_hour * cfg.POINTS_PER_HOUR))
        return np.array(indices1 + indices2)
    else:
        # Normal period
        return np.arange(start_hour * cfg.POINTS_PER_HOUR, end_hour * cfg.POINTS_PER_HOUR)


def detect_hypoglycemia_patterns(p10, p25, p50, sections, patterns):
    """Detect hypoglycemia patterns by time period."""
    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_p25 = p25[indices]
            period_p10 = p10[indices]

            # Check if median dips below threshold
            if np.min(period_p50) < cfg.HYPO_THRESHOLD:
                patterns.append(f"Consistent hypoglycemia during {name} period")
            elif np.min(period_p10) < cfg.SEVERE_HYPO_THRESHOLD:
                patterns.append(f"Sporadic, very dangerous hypoglycemia during {name} period")
            elif np.min(period_p25) < cfg.HYPO_THRESHOLD:
                patterns.append(f"Recurring hypoglycemia during {name} period")


def detect_hyperglycemia_patterns(p50, p75, sections, patterns):
    """Detect hyperglycemia patterns by time period."""
    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_p75 = p75[indices]

            if np.mean(period_p50) > cfg.VERY_HIGH:
                patterns.append(f"Very high glucose during {name} period")
            elif np.mean(period_p50) > cfg.TARGET_HIGH:
                patterns.append(f"Elevated glucose during {name} period")
            elif np.mean(period_p75) > cfg.TARGET_HIGH:
                patterns.append(f"Frequent glucose elevations during {name} period")


def detect_meal_spikes(p50, patterns):
    """Detect post-meal glucose spikes."""
    meal_configs = [
        ("breakfast", cfg.BREAKFAST_PRE_HOUR, cfg.BREAKFAST_START_HOUR, cfg.BREAKFAST_END_HOUR),
        ("lunch", cfg.LUNCH_PRE_HOUR, cfg.LUNCH_START_HOUR, cfg.LUNCH_END_HOUR),
        ("dinner", cfg.DINNER_PRE_HOUR, cfg.DINNER_START_HOUR, cfg.DINNER_END_HOUR),
    ]
    
    for meal_name, pre_hour, start_hour, end_hour in meal_configs:
        pre_idx = pre_hour * cfg.POINTS_PER_HOUR
        start_idx = start_hour * cfg.POINTS_PER_HOUR
        end_idx = end_hour * cfg.POINTS_PER_HOUR
        
        if end_idx <= len(p50):
            pre_meal = np.mean(p50[pre_idx:start_idx])
            post_meal = np.max(p50[start_idx:end_idx])
            if post_meal - pre_meal > cfg.MEAL_SPIKE_THRESHOLD:
                patterns.append(f"Post-{meal_name} glucose spike")


def detect_dawn_phenomenon(p50, patterns):
    """Detect dawn phenomenon - glucose rises in early morning."""
    dawn_start_idx = cfg.DAWN_START_HOUR * cfg.POINTS_PER_HOUR
    dawn_end_idx = cfg.DAWN_END_HOUR * cfg.POINTS_PER_HOUR
    
    dawn_start_glucose = np.mean(p50[dawn_start_idx : dawn_start_idx + 6])
    dawn_end_glucose = np.mean(p50[dawn_end_idx - 6 : dawn_end_idx])
    dawn_rise = dawn_end_glucose - dawn_start_glucose
    
    if dawn_rise > cfg.DAWN_RISE_THRESHOLD:
        patterns.append("Dawn phenomenon detected")


def detect_somogyi_effect(p50, patterns):
    """Detect Somogyi effect - rebound hyperglycemia after nocturnal hypoglycemia."""
    early_night_idx = cfg.SOMOGYI_NIGHT_START_HOUR * cfg.POINTS_PER_HOUR
    early_night_end = cfg.SOMOGYI_NIGHT_END_HOUR * cfg.POINTS_PER_HOUR
    morning_idx = cfg.SOMOGYI_MORNING_START_HOUR * cfg.POINTS_PER_HOUR
    morning_end = cfg.SOMOGYI_MORNING_END_HOUR * cfg.POINTS_PER_HOUR
    
    early_night_min = np.min(p50[early_night_idx:early_night_end])
    morning_glucose = np.mean(p50[morning_idx:morning_end])
    
    if early_night_min < cfg.HYPO_THRESHOLD and morning_glucose > cfg.TARGET_HIGH:
        patterns.append("Possible rebound hyperglycemia (Somogyi effect)")


def detect_fasting_patterns(p50, iqr, patterns):
    """Detect fasting glucose patterns."""
    fasting_start_idx = cfg.FASTING_START_HOUR * cfg.POINTS_PER_HOUR
    fasting_end_idx = cfg.FASTING_END_HOUR * cfg.POINTS_PER_HOUR
    
    fasting_p50 = p50[fasting_start_idx:fasting_end_idx]
    fasting_median = np.mean(fasting_p50)
    fasting_iqr = np.mean(iqr[fasting_start_idx:fasting_end_idx])
    
    if fasting_median > cfg.FASTING_TARGET_HIGH:
        patterns.append("Elevated fasting glucose levels")
    elif (
        cfg.FASTING_OPTIMAL_LOW <= fasting_median <= cfg.FASTING_OPTIMAL_HIGH
        and fasting_iqr < cfg.TIGHT_IQR
    ):
        patterns.append("Optimal fasting glucose control")
    elif fasting_median < cfg.FASTING_OPTIMAL_LOW:
        patterns.append("Low fasting glucose levels")


def analyze_meal_response(p50, pre_idx, meal_start_idx, meal_end_idx, meal_name, patterns):
    """Analyze detailed meal response pattern."""
    # 1. Pre-meal baseline
    baseline = np.mean(p50[pre_idx:meal_start_idx])
    
    # 2. Peak glucose and time to peak
    post_meal_window = p50[meal_start_idx:meal_end_idx]
    peak_glucose = np.max(post_meal_window)
    peak_idx_relative = np.argmax(post_meal_window)
    time_to_peak_minutes = peak_idx_relative * 5  # 5-min intervals
    
    # 3. Rise magnitude
    glucose_rise = peak_glucose - baseline
    
    # 4. Duration of elevation
    elevated_threshold = baseline + cfg.ELEVATION_THRESHOLD_OFFSET
    elevated_count = np.sum(post_meal_window > elevated_threshold)
    duration_elevated_minutes = elevated_count * 5
    
    # 5. Return to baseline
    recovery_window = p50[meal_end_idx - 6 : meal_end_idx]
    final_glucose = np.mean(recovery_window)
    returns_to_baseline = abs(final_glucose - baseline) < cfg.RECOVERY_THRESHOLD
    
    # Detect patterns
    if (
        time_to_peak_minutes < cfg.RAPID_SPIKE_TIME_THRESHOLD
        and glucose_rise > cfg.RAPID_SPIKE_RISE_THRESHOLD
    ):
        patterns.append(f"Rapid post-{meal_name} glucose spike")
    
    if duration_elevated_minutes > cfg.PROLONGED_ELEVATION_DURATION:
        patterns.append(f"Extended post-{meal_name} elevation")
    
    if (
        not returns_to_baseline
        and final_glucose > baseline + cfg.RECOVERY_THRESHOLD_DELAYED
    ):
        patterns.append(f"Slow post-{meal_name} glucose recovery")
    
    if (
        cfg.GOOD_MEAL_RISE_MIN < glucose_rise < cfg.GOOD_MEAL_RISE_MAX
        and cfg.GOOD_MEAL_PEAK_TIME_MIN < time_to_peak_minutes < cfg.GOOD_MEAL_PEAK_TIME_MAX
        and returns_to_baseline
    ):
        patterns.append(f"Well-controlled post-{meal_name} glucose response")


def detect_meal_response_patterns(p50, patterns):
    """Detect post-meal response quality patterns."""
    meal_configs = [
        ("breakfast", cfg.BREAKFAST_PRE_HOUR, cfg.BREAKFAST_START_HOUR, cfg.BREAKFAST_END_HOUR),
        ("lunch", cfg.LUNCH_PRE_HOUR, cfg.LUNCH_START_HOUR, cfg.LUNCH_END_HOUR),
        ("dinner", cfg.DINNER_PRE_HOUR, cfg.DINNER_START_HOUR, cfg.DINNER_END_HOUR),
    ]
    
    for meal_name, pre_hour, start_hour, end_hour in meal_configs:
        pre_h = pre_hour * cfg.POINTS_PER_HOUR
        start_h = start_hour * cfg.POINTS_PER_HOUR
        end_h = end_hour * cfg.POINTS_PER_HOUR
        
        if end_h <= len(p50):
            analyze_meal_response(p50, pre_h, start_h, end_h, meal_name, patterns)


def detect_variability_patterns(iqr, sections, patterns):
    """Detect glucose variability patterns."""
    for name, indices in sections.items():
        if len(indices) > 0:
            period_iqr = iqr[indices]
            if np.mean(period_iqr) > cfg.WIDE_IQR:
                patterns.append(f"High glucose variability during {name} period")


def detect_tight_control(p50, iqr, sections, patterns):
    """Detect periods of tight glucose control."""
    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_iqr = iqr[indices]
            
            median_in_optimal = cfg.OPTIMAL_LOW <= np.mean(period_p50) <= cfg.OPTIMAL_HIGH
            tight_variability = np.mean(period_iqr) < cfg.TIGHT_IQR
            
            if median_in_optimal and tight_variability:
                patterns.append(f"Tight glucose control during {name} period")


def detect_overall_patterns(p50, iqr, patterns):
    """Detect overall glucose patterns."""
    overall_median = np.mean(p50)
    overall_iqr = np.mean(iqr)
    
    if cfg.OPTIMAL_LOW <= overall_median <= cfg.OPTIMAL_HIGH and overall_iqr < cfg.TIGHT_IQR:
        patterns.append("Excellent overall glucose control")
    elif overall_median < cfg.HYPO_THRESHOLD:
        patterns.append("Overall glucose trending low")
    elif overall_median > cfg.TARGET_HIGH:
        patterns.append("Overall glucose trending high")


def detect_consistency_patterns(outer_band, sections, patterns):
    """Detect time-of-day consistency patterns."""
    for name, indices in sections.items():
        if len(indices) > 0:
            period_outer_band = outer_band[indices]
            avg_outer_band = np.mean(period_outer_band)
            
            if avg_outer_band > cfg.CONSISTENCY_THRESHOLD:
                patterns.append(f"Inconsistent glucose patterns during {name} period")
            elif avg_outer_band < cfg.CONSISTENT_OUTER_BAND:
                patterns.append(f"Consistent glucose patterns during {name} period")


def detect_agp_patterns(agp_data: dict):
    """
    Extract notable patterns from AGP data.

    Args:
        agp_data: AGP dict with keys p10, p25, p50, p75, p90, time (288 points)

    Returns:
        list: Short human-readable pattern strings, or None if no data
    """
    if not agp_data or "p50" not in agp_data:
        return None

    p10 = np.array(agp_data["p10"])
    p25 = np.array(agp_data["p25"])
    p50 = np.array(agp_data["p50"])
    p75 = np.array(agp_data["p75"])
    p90 = np.array(agp_data["p90"])

    patterns = []

    # Calculate metrics
    iqr = p75 - p25  # Interquartile range
    outer_band = p90 - p10  # Outer band

    # Create sections dictionary
    sections = {}
    for name, (start, end) in cfg.TIME_PERIODS.items():
        sections[name] = get_period_indices(start, end)

    # Run all pattern detection functions
    detect_hypoglycemia_patterns(p10, p25, p50, sections, patterns)
    detect_hyperglycemia_patterns(p50, p75, sections, patterns)
    detect_meal_spikes(p50, patterns)
    detect_dawn_phenomenon(p50, patterns)
    detect_somogyi_effect(p50, patterns)
    detect_fasting_patterns(p50, iqr, patterns)
    detect_meal_response_patterns(p50, patterns)
    detect_variability_patterns(iqr, sections, patterns)
    detect_tight_control(p50, iqr, sections, patterns)
    detect_overall_patterns(p50, iqr, patterns)
    detect_consistency_patterns(outer_band, sections, patterns)

    return patterns if patterns else None
