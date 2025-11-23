from datetime import datetime, timedelta

from charts.charts.util import (
    find_closest_time_index,
    timestrings_to_numeric,
)


def rotate_agp_chart_data(
    time_labels: list,
    p10: list,
    p25: list,
    p50: list,
    p75: list,
    p90: list,
    end_timestamp: str,
) -> tuple:
    """Rotate AGP data arrays based on end_timestamp."""

    def interpolate(a, b):
        return (a + b) / 2

    def interpolate_time_label(t1, t2):
        dt1 = datetime.strptime(t1, "%H:%M")
        dt2 = datetime.strptime(t2, "%H:%M")
        # handle midnight wrap
        if dt2 < dt1:
            dt2 += timedelta(days=1)
        avg_dt = dt1 + (dt2 - dt1) / 2
        return avg_dt.strftime("%H:%M")

    rotation_hours = 0

    if end_timestamp != "00:00":
        try:
            end_time = datetime.strptime(end_timestamp, "%H:%M")
            rotation_hours = end_time.hour + end_time.minute / 60.0
            end_index = find_closest_time_index(
                time_labels, end_time.hour, end_time.minute
            )

            if end_index > 0:
                # Interpolate for time_labels (assume string times, so just duplicate end_index value)
                time_labels = (
                    time_labels[end_index:-1]
                    + [interpolate_time_label(time_labels[-2], time_labels[0])]
                    + time_labels[:end_index]
                )
                p10 = (
                    p10[end_index:-1] + [interpolate(p10[-2], p10[0])] + p10[:end_index]
                )
                p25 = (
                    p25[end_index:-1] + [interpolate(p25[-2], p25[0])] + p25[:end_index]
                )
                p50 = (
                    p50[end_index:-1] + [interpolate(p50[-2], p50[0])] + p50[:end_index]
                )
                p75 = (
                    p75[end_index:-1] + [interpolate(p75[-2], p75[0])] + p75[:end_index]
                )
                p90 = (
                    p90[end_index:-1] + [interpolate(p90[-2], p90[0])] + p90[:end_index]
                )
        except ValueError:
            pass

    return time_labels, p10, p25, p50, p75, p90, rotation_hours


def extend_agp_chart_data(
    time_labels: list,
    p10: list,
    p25: list,
    p50: list,
    p75: list,
    p90: list,
    extend_hours: int,
) -> tuple:
    """Extend AGP data arrays by duplicating the first N hours at the end."""
    if extend_hours > 0:
        points_per_hour = len(time_labels) // 24
        points_for_extend = points_per_hour * extend_hours

        time_labels = time_labels + time_labels[:points_for_extend]
        p10 = p10 + p10[:points_for_extend]
        p25 = p25 + p25[:points_for_extend]
        p50 = p50 + p50[:points_for_extend]
        p75 = p75 + p75[:points_for_extend]
        p90 = p90 + p90[:points_for_extend]

    return time_labels, p10, p25, p50, p75, p90


def get_agp_chart_data(
    agp_data: dict,
    start_timestamp: datetime = datetime.strptime("00:00", "%H:%M"),
    end_timestamp: datetime = datetime.strptime("00:00", "%H:%M"),
    extend_hours: int = 0,
) -> dict:
    # Convert end_timestamp to string for processing
    end_timestamp_str = end_timestamp.strftime("%H:%M")

    # Extract and prepare data
    time_labels = agp_data.get("time", [])
    p10 = agp_data.get("p10", [])
    p25 = agp_data.get("p25", [])
    p50 = agp_data.get("p50", [])
    p75 = agp_data.get("p75", [])
    p90 = agp_data.get("p90", [])

    # Rotate data to start/end at specified timestamp
    time_labels, p10, p25, p50, p75, p90, rotation_hours = rotate_agp_chart_data(
        time_labels, p10, p25, p50, p75, p90, end_timestamp_str
    )

    # Extend data for additional hours if requested
    time_labels, p10, p25, p50, p75, p90 = extend_agp_chart_data(
        time_labels, p10, p25, p50, p75, p90, extend_hours
    )

    return {
        "time_labels": time_labels,
        "x_values": timestrings_to_numeric(time_labels, start_timestamp),
        "p10": p10,
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p90": p90,
        "rotation_hours": rotation_hours,
    }
