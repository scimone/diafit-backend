# filepath: c:\Users\anna_\Git Projects\diafit-backend\summary\util\calculate_agp.py

import numpy as np
import pandas as pd
from scipy import interpolate as interp


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

    # Extract the time grouping component
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


def calculate_agp(logs, log_type="cgm", smoothed=True, points_per_day=288):
    """
    Calculate Ambulatory Glucose Profile (AGP) with specified number of points per day.

    Args:
        logs: Log data to analyze (queryset or list of dicts)
        log_type: Type of log to process (default 'cgm')
        smoothed: Whether to apply smoothing to the percentile curves (default True)
        points_per_day: Number of points per day (default 288 for 5-min intervals)

    Returns:
        tuple: (time_array, p10, p25, p50, p75, p90) - time points and percentile values
    """
    # Calculate hourly statistics
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


def calculate_agp_from_cgm(cgm_queryset, smoothed=True):
    """
    Calculate AGP from CGM queryset and return formatted JSON.

    Args:
        cgm_queryset: Django queryset of CGM data
        smoothed: Whether to apply smoothing (default True)

    Returns:
        dict or None: Formatted AGP data or None if insufficient data
    """
    if not cgm_queryset.exists():
        return None

    try:
        result = calculate_agp(cgm_queryset, log_type="cgm", smoothed=smoothed)
        if result is None:
            return None

        return format_agp_json(*result)
    except Exception as e:
        print(f"Error calculating AGP: {e}")
        return None
