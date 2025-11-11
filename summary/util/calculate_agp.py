# filepath: c:\Users\anna_\Git Projects\diafit-backend\summary\util\calculate_agp.py

import numpy as np
import pandas as pd
import pytz
from scipy import interpolate as interp

# Default timezone for users
DEFAULT_TIMEZONE = pytz.timezone("Europe/Berlin")

# Shared time period definitions (in hours)
TIME_PERIODS = {
    "night": (22, 7),  # 22:00 - 07:00 (wraps around midnight)
    "morning": (7, 11),  # 07:00 - 11:00
    "noon": (11, 15),  # 11:00 - 15:00
    "afternoon": (15, 18),  # 15:00 - 18:00
    "evening": (18, 22),  # 18:00 - 22:00
}


def calculate_stats(logs, log_type, time_grouping="hour"):
    """
    Calculate percentile statistics from log data grouped by time period.

    Args:
        logs: List of dictionaries or queryset with timestamp and value data
        log_type: Type of log ('cgm', 'bolus', etc.)
        time_grouping: Time period to group by ('hour', 'day', etc.)

    Returns:
        pandas.DataFrame: DataFrame with percentile statistics (p_10, p_25, p_50, p_75, p_90)
                         indexed by the time grouping
    """
    if not logs:
        return pd.DataFrame()

    # Determine the timestamp and value columns based on log_type
    if log_type == "cgm":
        timestamp_col = "timestamp"
        value_col = "value_mgdl"
    elif log_type == "bolus":
        timestamp_col = "timestamp_utc"
        value_col = "value"
    else:
        # Generic fallback
        timestamp_col = "timestamp"
        value_col = "value"

    # Convert logs to DataFrame
    if hasattr(logs, "values"):
        # It's a Django queryset - select only needed columns
        df = pd.DataFrame(list(logs.values(timestamp_col, value_col)))
    else:
        # It's already a list
        df = pd.DataFrame(logs)

    if df.empty:
        return pd.DataFrame()

    # Convert timestamp to datetime if it's not already
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # Convert to user's timezone (timestamps are stored in UTC)
    if df[timestamp_col].dt.tz is None:
        # If timestamps are naive, assume UTC
        df[timestamp_col] = df[timestamp_col].dt.tz_localize("UTC")

    # Convert to user's local timezone
    df[timestamp_col] = df[timestamp_col].dt.tz_convert(DEFAULT_TIMEZONE)

    # Extract the time grouping component (now in user's local time)
    if time_grouping == "hour":
        df["group"] = df[timestamp_col].dt.hour
    elif time_grouping == "day":
        df["group"] = df[timestamp_col].dt.date
    elif time_grouping == "week":
        df["group"] = df[timestamp_col].dt.isocalendar().week
    elif time_grouping == "month":
        df["group"] = df[timestamp_col].dt.month
    else:
        df["group"] = df[timestamp_col].dt.hour

    # Calculate percentiles for each group
    stats = df.groupby("group")[value_col].agg(
        [
            ("p_10", lambda x: x.quantile(0.10)),
            ("p_25", lambda x: x.quantile(0.25)),
            ("p_50", lambda x: x.quantile(0.50)),
            ("p_75", lambda x: x.quantile(0.75)),
            ("p_90", lambda x: x.quantile(0.90)),
        ]
    )

    # If grouping by hour, ensure all 24 hours are present
    if time_grouping == "hour":
        all_hours = pd.DataFrame(index=range(24))
        stats = all_hours.join(stats, how="left")
        # Fill missing hours with interpolation or forward/backward fill
        stats = stats.interpolate(method="linear", limit_direction="both")

    return stats


def calculate_agp(
    logs, log_type="cgm", smoothed=True, points_per_day=288, user_timezone=None
):
    """
    Calculate Ambulatory Glucose Profile (AGP) with specified number of points per day.

    Args:
        logs: Log data to analyze (queryset or list of dicts)
        log_type: Type of log to process (default 'cgm')
        smoothed: Whether to apply smoothing to the percentile curves (default True)
        points_per_day: Number of points per day (default 288 for 5-min intervals)
        user_timezone: User's timezone (default None uses Europe/Berlin)

    Returns:
        tuple: (time_array, p10, p25, p50, p75, p90) - time points and percentile values
    """
    # Set timezone globally for this calculation
    original_tz = None
    if user_timezone:
        global DEFAULT_TIMEZONE
        original_tz = DEFAULT_TIMEZONE
        DEFAULT_TIMEZONE = (
            pytz.timezone(user_timezone)
            if isinstance(user_timezone, str)
            else user_timezone
        )

    try:
        # Calculate hourly statistics (will use DEFAULT_TIMEZONE)
        stats = calculate_stats(logs, log_type, "hour")
        if stats.empty:
            return None

        stats = stats.sort_index()

        # Extract percentiles
        percentiles = {}
        for p in ["p_10", "p_25", "p_50", "p_75", "p_90"]:
            values = stats[p].values

            # Apply smoothing if requested
            if smoothed:
                smoothed_values = np.convolve(
                    values, np.array([1.0, 4.0, 1.0]) / 6.0, "valid"
                )
                values = np.append(np.append(values[0], smoothed_values), values[-1])

            # Add periodic boundary condition (wrap around to start)
            percentiles[p] = np.append(values, values[0])

        # Hours with periodic boundary
        hours = np.append(list(stats.index), 24)

        # Interpolate to get 288 points per day
        time_array = np.linspace(0, 24, points_per_day)
        interpolated = {}

        for p, values in percentiles.items():
            spline = interp.CubicSpline(hours, values, bc_type="periodic")
            interpolated[p] = spline(time_array)

        return (
            time_array,
            interpolated["p_10"],
            interpolated["p_25"],
            interpolated["p_50"],
            interpolated["p_75"],
            interpolated["p_90"],
        )
    finally:
        # Restore original timezone if it was changed
        if original_tz is not None:
            DEFAULT_TIMEZONE = original_tz


def format_agp_json(time_array, p10, p25, p50, p75, p90):
    """
    Format AGP data into JSON structure for storage.

    Args:
        time_array: Time points in hours (0-24)
        p10, p25, p50, p75, p90: Percentile arrays

    Returns:
        dict: Formatted AGP data with time labels and percentiles
    """
    time_labels = [f"{int(t):02d}:{int((t % 1) * 60):02d}" for t in time_array]

    return {
        "time": time_labels,
        "p10": [round(float(v), 1) for v in p10],
        "p25": [round(float(v), 1) for v in p25],
        "p50": [round(float(v), 1) for v in p50],
        "p75": [round(float(v), 1) for v in p75],
        "p90": [round(float(v), 1) for v in p90],
    }


def calculate_agp_summary(agp_data):
    """
    Calculate AGP summary statistics by time period.

    Args:
        agp_data: Formatted AGP JSON data with time and percentile arrays

    Returns:
        dict or None: Summary statistics by period (night, morning, lunch, afternoon, evening)
    """
    if not agp_data or "time" not in agp_data:
        return None

    summary = {}

    for period_name, (start_hour, end_hour) in TIME_PERIODS.items():
        # Find indices for this time period
        indices = []
        for i, time_str in enumerate(agp_data["time"]):
            hour = int(time_str.split(":")[0])

            # Handle periods that wrap around midnight
            if start_hour > end_hour:
                # Period wraps around midnight (e.g., 22:00 - 07:00)
                if hour >= start_hour or hour < end_hour:
                    indices.append(i)
            else:
                # Normal period
                if start_hour <= hour < end_hour:
                    indices.append(i)

        if not indices:
            continue

        # Extract percentile values for this period
        p10_values = [agp_data["p10"][i] for i in indices]
        p25_values = [agp_data["p25"][i] for i in indices]
        p50_values = [agp_data["p50"][i] for i in indices]
        p75_values = [agp_data["p75"][i] for i in indices]
        p90_values = [agp_data["p90"][i] for i in indices]

        # Calculate average ranges and median for the period
        summary[period_name] = {
            "p10_p90_range": [
                round(sum(p10_values) / len(p10_values), 1),
                round(sum(p90_values) / len(p90_values), 1),
            ],
            "p25_p75_range": [
                round(sum(p25_values) / len(p25_values), 1),
                round(sum(p75_values) / len(p75_values), 1),
            ],
            "p50": round(sum(p50_values) / len(p50_values), 1),
        }

    return summary if summary else None


def calculate_agp_from_cgm(cgm_queryset, smoothed=True, user_timezone=None):
    """
    Calculate AGP from CGM queryset and return formatted JSON.

    Args:
        cgm_queryset: Django queryset of CGM data
        smoothed: Whether to apply smoothing (default True)
        user_timezone: User's timezone (default None uses Europe/Berlin)

    Returns:
        dict or None: Formatted AGP data or None if insufficient data
    """
    if not cgm_queryset.exists():
        return None

    try:
        result = calculate_agp(
            cgm_queryset, log_type="cgm", smoothed=smoothed, user_timezone=user_timezone
        )
        if result is None:
            return None

        return format_agp_json(*result)
    except Exception as e:
        print(f"Error calculating AGP: {e}")
        return None


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

    # ========================================================================
    # CONFIGURATION - All thresholds and time windows
    # ========================================================================

    # Time configuration
    POINTS_PER_HOUR = 12  # 5-min intervals: 60/5 = 12 points per hour

    # Clinical glucose thresholds (mg/dL)
    HYPO_THRESHOLD = 70  # Hypoglycemia threshold
    SEVERE_HYPO_THRESHOLD = 54  # Severe hypoglycemia threshold
    TARGET_LOW = 70  # General target range low
    TARGET_HIGH = 180  # General target range high
    VERY_HIGH = 250  # Very high glucose threshold
    OPTIMAL_LOW = 70  # Optimal range low
    OPTIMAL_HIGH = 140  # Optimal range high

    # Fasting glucose thresholds (mg/dL)
    FASTING_OPTIMAL_LOW = 70
    FASTING_OPTIMAL_HIGH = 100  # Stricter for fasting
    FASTING_TARGET_HIGH = 130  # Maximum acceptable fasting

    # Variability thresholds (mg/dL)
    WIDE_IQR = 60  # High daily variability threshold
    TIGHT_IQR = 30  # Tight control threshold
    CONSISTENCY_THRESHOLD = 100  # Outer band threshold for consistency
    CONSISTENT_OUTER_BAND = 40  # Very narrow outer band

    # Meal spike thresholds
    MEAL_SPIKE_THRESHOLD = 50  # mg/dL rise for meal spike detection

    # Dawn phenomenon
    DAWN_START_HOUR = 3  # Start of dawn phenomenon window
    DAWN_END_HOUR = 7  # End of dawn phenomenon window
    DAWN_RISE_THRESHOLD = 20  # mg/dL rise to detect dawn phenomenon

    # Somogyi effect
    SOMOGYI_NIGHT_START_HOUR = 2  # Early night low check start
    SOMOGYI_NIGHT_END_HOUR = 4  # Early night low check end
    SOMOGYI_MORNING_START_HOUR = 6  # Morning rebound check start
    SOMOGYI_MORNING_END_HOUR = 8  # Morning rebound check end

    # Fasting glucose window
    FASTING_START_HOUR = 5  # Fasting glucose window start
    FASTING_END_HOUR = 7  # Fasting glucose window end

    # Meal timing windows (hours)
    BREAKFAST_PRE_HOUR = 6
    BREAKFAST_START_HOUR = 7
    BREAKFAST_END_HOUR = 10

    LUNCH_PRE_HOUR = 11
    LUNCH_START_HOUR = 12
    LUNCH_END_HOUR = 15

    DINNER_PRE_HOUR = 18
    DINNER_START_HOUR = 19
    DINNER_END_HOUR = 22

    # Meal response quality thresholds
    RAPID_SPIKE_TIME_THRESHOLD = 30  # minutes - rapid spike if peak <30 min
    RAPID_SPIKE_RISE_THRESHOLD = 50  # mg/dL - rapid spike if rise >50
    PROLONGED_ELEVATION_DURATION = 90  # minutes - prolonged if elevated >90 min
    ELEVATION_THRESHOLD_OFFSET = 30  # mg/dL above baseline to consider "elevated"
    RECOVERY_THRESHOLD = 20  # mg/dL from baseline to consider "recovered"
    RECOVERY_THRESHOLD_DELAYED = 30  # mg/dL from baseline for delayed recovery

    # Good meal response criteria
    GOOD_MEAL_RISE_MIN = 20  # mg/dL minimum rise
    GOOD_MEAL_RISE_MAX = 40  # mg/dL maximum rise
    GOOD_MEAL_PEAK_TIME_MIN = 30  # minutes minimum time to peak
    GOOD_MEAL_PEAK_TIME_MAX = 90  # minutes maximum time to peak

    # Consistency check windows
    MORNING_CONSISTENCY_START_HOUR = 7
    MORNING_CONSISTENCY_END_HOUR = 9
    BEDTIME_CONSISTENCY_START_HOUR = 21
    BEDTIME_CONSISTENCY_END_HOUR = 23
    INCONSISTENT_MORNING_THRESHOLD = 100  # mg/dL outer band
    INCONSISTENT_BEDTIME_THRESHOLD = 100  # mg/dL outer band

    # Overnight stability
    STABLE_NIGHT_IQR = 25  # mg/dL - stable if IQR < 25
    FLUCTUATING_NIGHT_IQR = 50  # mg/dL - fluctuating if IQR > 50

    # ========================================================================
    # END CONFIGURATION
    # ========================================================================

    # Basic metrics
    iqr = p75 - p25  # Interquartile range (25-75% band) - daily variation
    outer_band = p90 - p10  # Outer band (10-90%) - occasional fluctuations

    # Helper function to get indices for a time period (handles wraparound)
    def get_period_indices(start_hour, end_hour):
        if start_hour > end_hour:
            # Wraps around midnight (e.g., 22-7)
            indices1 = list(range(start_hour * POINTS_PER_HOUR, 24 * POINTS_PER_HOUR))
            indices2 = list(range(0, end_hour * POINTS_PER_HOUR))
            return np.array(indices1 + indices2)
        else:
            # Normal period
            return np.arange(start_hour * POINTS_PER_HOUR, end_hour * POINTS_PER_HOUR)

    # Create sections dictionary with proper indices
    sections = {}
    for name, (start, end) in TIME_PERIODS.items():
        sections[name] = get_period_indices(start, end)

    # ========================================================================
    # A. HYPOGLYCEMIA PATTERNS (Time Below Range)
    # Look for median or IQR dipping below 70 mg/dL
    # ========================================================================

    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_p25 = p25[indices]

            # Check if median dips below threshold
            if np.min(period_p50) < HYPO_THRESHOLD:
                patterns.append(f"Low glucose during {name} period")

            # Check if p25 (lower IQR boundary) is below threshold
            elif np.min(period_p25) < HYPO_THRESHOLD:
                patterns.append(f"Frequent low readings during {name} period")

    # Specific overnight hypoglycemia risk
    if "night" in sections and len(sections["night"]) > 0:
        night_p10 = np.min(p10[sections["night"]])
        night_p25 = np.min(p25[sections["night"]])

        if night_p10 < SEVERE_HYPO_THRESHOLD:
            patterns.append("Risk of severe overnight hypoglycemia")
        elif night_p25 < HYPO_THRESHOLD:
            patterns.append("Risk of overnight hypoglycemia")

    # ========================================================================
    # B. HYPERGLYCEMIA PATTERNS (Time Above Range)
    # Median or IQR consistently above 180 mg/dL
    # ========================================================================

    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_p75 = p75[indices]

            # Check for very high median
            if np.mean(period_p50) > VERY_HIGH:
                patterns.append(f"Very high glucose during {name} period")

            # Check if median consistently above target
            elif np.mean(period_p50) > TARGET_HIGH:
                patterns.append(f"Elevated glucose during {name} period")

            # Check if p75 (upper IQR boundary) consistently above target
            elif np.mean(period_p75) > TARGET_HIGH:
                patterns.append(f"Frequent glucose elevations during {name} period")

    # Specific meal-related spikes (check for significant rises)
    # Post-breakfast spike
    breakfast_start_idx = BREAKFAST_START_HOUR * POINTS_PER_HOUR
    breakfast_end_idx = BREAKFAST_END_HOUR * POINTS_PER_HOUR
    pre_breakfast_idx = BREAKFAST_PRE_HOUR * POINTS_PER_HOUR

    if breakfast_end_idx <= len(p50):
        pre_breakfast = np.mean(p50[pre_breakfast_idx:breakfast_start_idx])
        post_breakfast = np.max(p50[breakfast_start_idx:breakfast_end_idx])
        if post_breakfast - pre_breakfast > MEAL_SPIKE_THRESHOLD:
            patterns.append("Post-breakfast glucose spike")

    # Post-lunch spike
    lunch_start_idx = LUNCH_START_HOUR * POINTS_PER_HOUR
    lunch_end_idx = LUNCH_END_HOUR * POINTS_PER_HOUR
    pre_lunch_idx = LUNCH_PRE_HOUR * POINTS_PER_HOUR

    if lunch_end_idx <= len(p50):
        pre_lunch = np.mean(p50[pre_lunch_idx:lunch_start_idx])
        post_lunch = np.max(p50[lunch_start_idx:lunch_end_idx])
        if post_lunch - pre_lunch > MEAL_SPIKE_THRESHOLD:
            patterns.append("Post-lunch glucose spike")

    # Post-dinner spike
    dinner_start_idx = DINNER_START_HOUR * POINTS_PER_HOUR
    dinner_end_idx = DINNER_END_HOUR * POINTS_PER_HOUR
    pre_dinner_idx = DINNER_PRE_HOUR * POINTS_PER_HOUR

    if dinner_end_idx <= len(p50):
        pre_dinner = np.mean(p50[pre_dinner_idx:dinner_start_idx])
        post_dinner = np.max(p50[dinner_start_idx:dinner_end_idx])
        if post_dinner - pre_dinner > MEAL_SPIKE_THRESHOLD:
            patterns.append("Post-dinner glucose spike")

    # ========================================================================
    # F. DAWN PHENOMENON & SOMOGYI EFFECT
    # ========================================================================

    # Dawn phenomenon - glucose rises without eating (physiological)
    dawn_start_idx = DAWN_START_HOUR * POINTS_PER_HOUR
    dawn_end_idx = DAWN_END_HOUR * POINTS_PER_HOUR

    dawn_start_glucose = np.mean(
        p50[dawn_start_idx : dawn_start_idx + 6]
    )  # First 30 min
    dawn_end_glucose = np.mean(p50[dawn_end_idx - 6 : dawn_end_idx])  # Last 30 min
    dawn_rise = dawn_end_glucose - dawn_start_glucose

    if dawn_rise > DAWN_RISE_THRESHOLD:
        patterns.append("Dawn phenomenon detected")

    # Somogyi effect - rebound hyperglycemia after nocturnal hypoglycemia
    early_night_idx = SOMOGYI_NIGHT_START_HOUR * POINTS_PER_HOUR
    early_night_end = SOMOGYI_NIGHT_END_HOUR * POINTS_PER_HOUR
    morning_idx = SOMOGYI_MORNING_START_HOUR * POINTS_PER_HOUR
    morning_end = SOMOGYI_MORNING_END_HOUR * POINTS_PER_HOUR

    early_night_min = np.min(p50[early_night_idx:early_night_end])
    morning_glucose = np.mean(p50[morning_idx:morning_end])

    if early_night_min < HYPO_THRESHOLD and morning_glucose > TARGET_HIGH:
        patterns.append("Possible rebound hyperglycemia (Somogyi effect)")

    # ========================================================================
    # G. FASTING GLUCOSE PATTERNS
    # Early morning fasting glucose before typical breakfast
    # ========================================================================

    fasting_start_idx = FASTING_START_HOUR * POINTS_PER_HOUR
    fasting_end_idx = FASTING_END_HOUR * POINTS_PER_HOUR

    fasting_p50 = p50[fasting_start_idx:fasting_end_idx]
    fasting_median = np.mean(fasting_p50)
    fasting_iqr = np.mean(iqr[fasting_start_idx:fasting_end_idx])

    if fasting_median > FASTING_TARGET_HIGH:
        patterns.append("Elevated fasting glucose levels")
    elif (
        FASTING_OPTIMAL_LOW <= fasting_median <= FASTING_OPTIMAL_HIGH
        and fasting_iqr < TIGHT_IQR
    ):
        patterns.append("Optimal fasting glucose control")
    elif fasting_median < FASTING_OPTIMAL_LOW:
        patterns.append("Low fasting glucose levels")

    # ========================================================================
    # H. POST-MEAL PATTERN QUALITY
    # Analyze quality of glucose response after meals
    # ========================================================================

    def analyze_meal_response(pre_idx, meal_start_idx, meal_end_idx, meal_name):
        """Analyze detailed meal response pattern"""

        # 1. Pre-meal baseline
        baseline = np.mean(p50[pre_idx:meal_start_idx])

        # 2. Peak glucose and time to peak
        post_meal_window = p50[meal_start_idx:meal_end_idx]
        peak_glucose = np.max(post_meal_window)
        peak_idx_relative = np.argmax(post_meal_window)
        time_to_peak_minutes = peak_idx_relative * 5  # 5-min intervals

        # 3. Rise magnitude
        glucose_rise = peak_glucose - baseline

        # 4. Duration of elevation (how long >baseline + threshold)
        elevated_threshold = baseline + ELEVATION_THRESHOLD_OFFSET
        elevated_count = np.sum(post_meal_window > elevated_threshold)
        duration_elevated_minutes = elevated_count * 5

        # 5. Return to baseline (check last 30 min of window)
        recovery_window = p50[meal_end_idx - 6 : meal_end_idx]  # Last 30 min
        final_glucose = np.mean(recovery_window)
        returns_to_baseline = abs(final_glucose - baseline) < RECOVERY_THRESHOLD

        # Detect patterns
        # Rapid spike (peak quickly and high rise)
        if (
            time_to_peak_minutes < RAPID_SPIKE_TIME_THRESHOLD
            and glucose_rise > RAPID_SPIKE_RISE_THRESHOLD
        ):
            patterns.append(f"Rapid post-{meal_name} glucose spike")

        # Prolonged elevation (stays high for extended period)
        if duration_elevated_minutes > PROLONGED_ELEVATION_DURATION:
            patterns.append(f"Extended post-{meal_name} elevation")

        # Delayed recovery (doesn't return to baseline by end of window)
        if (
            not returns_to_baseline
            and final_glucose > baseline + RECOVERY_THRESHOLD_DELAYED
        ):
            patterns.append(f"Slow post-{meal_name} glucose recovery")

        # Good meal response (moderate rise, timely peak, good recovery)
        if (
            GOOD_MEAL_RISE_MIN < glucose_rise < GOOD_MEAL_RISE_MAX
            and GOOD_MEAL_PEAK_TIME_MIN < time_to_peak_minutes < GOOD_MEAL_PEAK_TIME_MAX
            and returns_to_baseline
        ):
            patterns.append(f"Well-controlled post-{meal_name} glucose response")

    # Analyze each meal
    # Breakfast
    breakfast_pre_h = BREAKFAST_PRE_HOUR * POINTS_PER_HOUR
    breakfast_start_h = BREAKFAST_START_HOUR * POINTS_PER_HOUR
    breakfast_end_h = BREAKFAST_END_HOUR * POINTS_PER_HOUR
    if breakfast_end_h <= len(p50):
        analyze_meal_response(
            breakfast_pre_h, breakfast_start_h, breakfast_end_h, "breakfast"
        )

    # Lunch
    lunch_pre_h = LUNCH_PRE_HOUR * POINTS_PER_HOUR
    lunch_start_h = LUNCH_START_HOUR * POINTS_PER_HOUR
    lunch_end_h = LUNCH_END_HOUR * POINTS_PER_HOUR
    if lunch_end_h <= len(p50):
        analyze_meal_response(lunch_pre_h, lunch_start_h, lunch_end_h, "lunch")

    # Dinner
    dinner_pre_h = DINNER_PRE_HOUR * POINTS_PER_HOUR
    dinner_start_h = DINNER_START_HOUR * POINTS_PER_HOUR
    dinner_end_h = DINNER_END_HOUR * POINTS_PER_HOUR
    if dinner_end_h <= len(p50):
        analyze_meal_response(dinner_pre_h, dinner_start_h, dinner_end_h, "dinner")

    # ========================================================================
    # C. GLUCOSE VARIABILITY
    # Wide IQR and outer bands = inconsistent control
    # ========================================================================

    for name, indices in sections.items():
        if len(indices) > 0:
            period_iqr = iqr[indices]

            # High daily variability (wide IQR)
            if np.mean(period_iqr) > WIDE_IQR:
                patterns.append(f"High glucose variability during {name} period")

    # ========================================================================
    # D. OPTIMAL OR TIGHT CONTROL
    # Median stays within 70-140 mg/dL, narrow IQR throughout
    # ========================================================================

    for name, indices in sections.items():
        if len(indices) > 0:
            period_p50 = p50[indices]
            period_iqr = iqr[indices]

            median_in_optimal = OPTIMAL_LOW <= np.mean(period_p50) <= OPTIMAL_HIGH
            tight_variability = np.mean(period_iqr) < TIGHT_IQR

            # Only report tight control if both conditions are met
            if median_in_optimal and tight_variability:
                patterns.append(f"Tight glucose control during {name} period")

    # ========================================================================
    # E. OVERALL PATTERNS
    # ========================================================================

    overall_median = np.mean(p50)
    overall_iqr = np.mean(iqr)

    # Excellent overall control
    if OPTIMAL_LOW <= overall_median <= OPTIMAL_HIGH and overall_iqr < TIGHT_IQR:
        patterns.append("Excellent overall glucose control")

    # Overall trending patterns
    elif overall_median < HYPO_THRESHOLD:
        patterns.append("Overall glucose trending low")
    elif overall_median > TARGET_HIGH:
        patterns.append("Overall glucose trending high")

    # ========================================================================
    # J. TIME-OF-DAY CONSISTENCY
    # Same-time-different-day variability (how consistent are patterns?)
    # ========================================================================

    # Check consistency for each time period using outer band width
    # Wide outer band = inconsistent day-to-day patterns
    # Narrow outer band = consistent patterns
    for name, indices in sections.items():
        if len(indices) > 0:
            period_outer_band = outer_band[indices]
            avg_outer_band = np.mean(period_outer_band)

            # High outer band width = inconsistent patterns
            if avg_outer_band > CONSISTENCY_THRESHOLD:
                patterns.append(f"Inconsistent glucose patterns during {name} period")

            # Very narrow outer band = very consistent
            elif avg_outer_band < CONSISTENT_OUTER_BAND:
                patterns.append(f"Consistent glucose patterns during {name} period")

    return patterns if patterns else None
