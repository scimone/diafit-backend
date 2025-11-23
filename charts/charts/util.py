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


def calculate_tick_positions(x_start_dt, x_end_hours):
    """
    Create tick positions every 3 hours for the new numeric x-axis.

    Parameters:
        x_start_dt (datetime): leftmost point of the x-axis
        x_end_hours (float): duration of the x-axis (in hours)

    Returns:
        (tick_vals, tick_labels)
    """
    tick_vals = []
    tick_labels = []

    # Create ticks at 0, 3, 6, ..., up to x_end_hours
    hour = 0
    while hour <= x_end_hours:
        tick_vals.append(hour)

        # Convert numeric hour back to actual clock time
        tick_dt = x_start_dt + timedelta(hours=hour)
        tick_labels.append(tick_dt.strftime("%H:%M"))

        hour += 3

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

    for t in time_list:
        # Handle 24:00 as midnight next day
        if t == "24:00":
            dt = prev_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )
        else:
            h, m = map(int, t.split(":"))
            # Build candidate on same day as previous
            dt = prev_dt.replace(hour=h, minute=m, second=0, microsecond=0)
            # If candidate <= previous, it wrapped past midnight → add 1 day
            if dt <= prev_dt:
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
