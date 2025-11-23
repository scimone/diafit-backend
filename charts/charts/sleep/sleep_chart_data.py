from charts.charts.util import datetimes_to_numeric


def get_sleep_chart_data(sleep_data, start_timestamp):
    sleep_starts = []
    sleep_ends = []

    for sleep_session in sleep_data:
        sleep_starts.append(sleep_session["start"])
        sleep_ends.append(sleep_session["end"])

    return {
        "sleep_start_x": datetimes_to_numeric(sleep_starts, start_timestamp),
        "sleep_end_x": datetimes_to_numeric(sleep_ends, start_timestamp),
    }
