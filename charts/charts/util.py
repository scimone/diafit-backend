from datetime import datetime, timedelta


def find_closest_time_index(
    time_labels: list, target_hour: int, target_minute: int
) -> int:
    """Find the index of the time label closest to the target time."""
    min_diff = float("inf")
    closest_index = 0
    target_minutes = target_hour * 60 + target_minute

    for i, time_str in enumerate(time_labels):
        try:
            t = datetime.strptime(time_str, "%H:%M")
            t_minutes = t.hour * 60 + t.minute
            diff = abs(t_minutes - target_minutes)
            if diff < min_diff:
                min_diff = diff
                closest_index = i
        except ValueError:
            continue

    return closest_index


def calculate_tick_positions(x_start_dt, x_end_dt, interval_hours=3):
    """
    Create tick positions for a numeric x-axis (hours since x_start_dt).

    Parameters:
        x_start_dt (datetime): leftmost point of the x-axis
        x_end_dt (datetime): rightmost point of the x-axis
        interval_hours (int): interval between ticks (default: 3)
        start_numeric (float): starting numeric value for ticks (default: 0)

    Returns:
        (tick_vals, tick_labels)
        tick_vals: list of numeric hour positions (e.g., [0, 3, 6, ...])
        tick_labels: list of corresponding 'HH:MM' strings
    """
    tick_vals = []
    tick_labels = []

    total_hours = (x_end_dt - x_start_dt).total_seconds() / 3600
    current = 0
    while current <= total_hours:
        tick_dt = x_start_dt + timedelta(hours=current)
        tick_vals.append(current)
        tick_labels.append(tick_dt.strftime("%H:%M"))
        current += interval_hours

    # Ensure last tick at x_end_dt if not already present
    if tick_vals[-1] < total_hours:
        tick_vals.append(total_hours)
        tick_labels.append(x_end_dt.strftime("%H:%M"))

    return tick_vals, tick_labels


def timestrings_to_numeric(time_list, x_start_dt):
    """
    Convert a list of 'HH:MM' strings to numeric hours relative to x_start_dt.
    Handles:
        - Midnight crossings
        - '24:00' as end-of-day
        - Multiple days
        - Strictly increasing numeric hours
    """

    numeric = []
    prev_dt = x_start_dt

    for idx, t in enumerate(time_list):
        # Handle 24:00 as midnight next day, but only if not the first timestamp
        if t == "24:00" and idx != 0:
            dt = prev_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )
        else:
            h, m = map(int, t.split(":"))
            # Build candidate on same day as previous
            dt = prev_dt.replace(hour=h, minute=m, second=0, microsecond=0)
            # If candidate <= previous, it wrapped past midnight → add 1 day
            if dt <= prev_dt and idx != 0:
                dt += timedelta(days=1)

        # Compute hours relative to x_start_dt
        delta_h = (dt - x_start_dt).total_seconds() / 3600
        numeric.append(delta_h)
        prev_dt = dt

    return numeric


def datetime_to_numeric(dt, x_start_dt):
    """
    Convert a single datetime object to numeric hours relative to x_start_dt (datetime).
    Handles crossing midnight automatically.
    dt: datetime object
    x_start_dt: starting time as a datetime object
    """
    delta_hours = (dt - x_start_dt).total_seconds() / 3600
    # if negative, assume it's the next day
    if delta_hours < 0:
        delta_hours += 24
    return delta_hours


def datetimes_to_numeric(datetime_list, x_start_dt):
    """
    Convert list of datetime objects to numeric hours relative to x_start_dt (datetime).
    Handles crossing midnight automatically.
    datetime_list: list of datetime objects
    x_start_dt: starting time as a datetime object
    """
    numeric_times = []
    for dt in datetime_list:
        delta_hours = datetime_to_numeric(dt, x_start_dt)
        numeric_times.append(delta_hours)
    return numeric_times
