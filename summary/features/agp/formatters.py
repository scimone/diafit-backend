"""
AGP Data Formatting Utilities
Functions for formatting AGP data for JSON output and API responses.
"""

from .calculations import calculate_agp


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
