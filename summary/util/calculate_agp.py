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

    # Basic metrics
    iqr = p75 - p25  # Interquartile range (25-75% band) - daily variation
    outer_band = p90 - p10  # Outer band (10-90%) - occasional fluctuations

    # Convert hour-based periods to index arrays (288 points = 12 points per hour)
    POINTS_PER_HOUR = 12  # 5-min intervals: 60/5 = 12 points per hour

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

    # Clinical thresholds
    HYPO_THRESHOLD = 70  # mg/dL
    SEVERE_HYPO_THRESHOLD = 54  # mg/dL
    TARGET_HIGH = 180  # mg/dL
    VERY_HIGH = 250  # mg/dL
    OPTIMAL_LOW = 70
    OPTIMAL_HIGH = 140

    # Variability thresholds
    WIDE_IQR = 60  # mg/dL - indicates high daily variability
    TIGHT_IQR = 30  # mg/dL - indicates tight control

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
    # Post-breakfast spike (7-10 AM)
    breakfast_start_idx = 7 * POINTS_PER_HOUR
    breakfast_end_idx = 10 * POINTS_PER_HOUR
    pre_breakfast_idx = 6 * POINTS_PER_HOUR

    if breakfast_end_idx <= len(p50):
        pre_breakfast = np.mean(p50[pre_breakfast_idx:breakfast_start_idx])
        post_breakfast = np.max(p50[breakfast_start_idx:breakfast_end_idx])
        if post_breakfast - pre_breakfast > 50:
            patterns.append("Post-breakfast glucose spike")

    # Post-lunch spike (13-15 PM)
    lunch_start_idx = 13 * POINTS_PER_HOUR
    lunch_end_idx = 15 * POINTS_PER_HOUR
    pre_lunch_idx = 12 * POINTS_PER_HOUR

    if lunch_end_idx <= len(p50):
        pre_lunch = np.mean(p50[pre_lunch_idx:lunch_start_idx])
        post_lunch = np.max(p50[lunch_start_idx:lunch_end_idx])
        if post_lunch - pre_lunch > 50:
            patterns.append("Post-lunch glucose spike")

    # Post-dinner spike (19-21 PM)
    dinner_start_idx = 19 * POINTS_PER_HOUR
    dinner_end_idx = 21 * POINTS_PER_HOUR
    pre_dinner_idx = 18 * POINTS_PER_HOUR

    if dinner_end_idx <= len(p50):
        pre_dinner = np.mean(p50[pre_dinner_idx:dinner_start_idx])
        post_dinner = np.max(p50[dinner_start_idx:dinner_end_idx])
        if post_dinner - pre_dinner > 50:
            patterns.append("Post-dinner glucose spike")

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

    return patterns if patterns else None
