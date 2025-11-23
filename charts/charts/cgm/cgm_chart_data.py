from charts.charts.util import datetimes_to_numeric
from core.colors import COLORS

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_cgm_chart_data(cgm_data, start_timestamp):
    target_lower, target_upper = TARGET_RANGE

    day_y = []
    day_colors = []
    timestamps = []

    for reading in cgm_data:
        day_y.append(reading["value"])
        timestamps.append(reading["timestamp"])

        value = reading["value"]
        if value < target_lower:
            day_colors.append(COLORS["diafit"]["under_range"])
        elif value > target_upper:
            day_colors.append(COLORS["diafit"]["above_range"])
        else:
            day_colors.append(COLORS["diafit"]["in_range"])

    return {
        "day_x": datetimes_to_numeric(timestamps, start_timestamp),
        "day_y": day_y,
        "day_colors": day_colors,
        "timestamps": timestamps,
    }
