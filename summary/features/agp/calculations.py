"""
Core AGP Calculation Functions
Statistical calculations and interpolation for Ambulatory Glucose Profile.
"""

import numpy as np
import pandas as pd
import pytz
from scipy import interpolate as interp

from .config import DEFAULT_TIMEZONE, POINTS_PER_DAY


def calculate_stats(logs, log_type, time_grouping="hour", user_timezone=None):
    """
    Calculate percentile statistics from log data grouped by time period.

    Args:
        logs: List of dictionaries or queryset with timestamp and value data
        log_type: Type of log ('cgm', 'bolus', etc.)
        time_grouping: Time period to group by ('hour', 'day', etc.)
        user_timezone: User's timezone (default None uses Europe/Berlin)

    Returns:
        pandas.DataFrame: DataFrame with percentile statistics (p_10, p_25, p_50, p_75, p_90)
                         indexed by the time grouping
    """
    if not logs:
        return pd.DataFrame()

    # Determine timezone
    tz = (
        pytz.timezone(user_timezone) if isinstance(user_timezone, str) else user_timezone
    ) if user_timezone else DEFAULT_TIMEZONE

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
    df[timestamp_col] = df[timestamp_col].dt.tz_convert(tz)

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
    logs, log_type="cgm", smoothed=True, points_per_day=POINTS_PER_DAY, user_timezone=None
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
    # Calculate hourly statistics
    stats = calculate_stats(logs, log_type, "hour", user_timezone)
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

    # Interpolate to get points_per_day points
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


def calculate_agp_summary(agp_data, time_periods):
    """
    Calculate AGP summary statistics by time period.

    Args:
        agp_data: Formatted AGP JSON data with time and percentile arrays
        time_periods: Dict of time period definitions {name: (start_hour, end_hour)}

    Returns:
        dict or None: Summary statistics by period
    """
    if not agp_data or "time" not in agp_data:
        return None

    summary = {}

    for period_name, (start_hour, end_hour) in time_periods.items():
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
