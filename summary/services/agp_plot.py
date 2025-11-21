# summary/services/agp_plot.py
import json
from datetime import datetime

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from core.colors import COLORS


def _find_closest_time_index(
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


def _rotate_agp_data(
    time_labels: list,
    p10: list,
    p25: list,
    p50: list,
    p75: list,
    p90: list,
    end_timestamp: str,
) -> tuple:
    """Rotate AGP data arrays based on end_timestamp."""
    rotation_hours = 0

    if end_timestamp != "00:00":
        try:
            end_time = datetime.strptime(end_timestamp, "%H:%M")
            rotation_hours = end_time.hour + end_time.minute / 60.0
            end_index = _find_closest_time_index(
                time_labels, end_time.hour, end_time.minute
            )

            if end_index > 0:
                time_labels = time_labels[end_index:] + time_labels[:end_index]
                p10 = p10[end_index:] + p10[:end_index]
                p25 = p25[end_index:] + p25[:end_index]
                p50 = p50[end_index:] + p50[:end_index]
                p75 = p75[end_index:] + p75[:end_index]
                p90 = p90[end_index:] + p90[:end_index]
        except ValueError:
            pass

    return time_labels, p10, p25, p50, p75, p90, rotation_hours


def _extend_agp_data(
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


def _add_percentile_bands(
    fig: go.Figure,
    x_values: list,
    p10: list,
    p25: list,
    p50: list,
    p75: list,
    p90: list,
    target_range: tuple,
):
    """Add all percentile bands to the figure."""
    target_lower, target_upper = target_range

    def clip_to_range(values, lower, upper):
        return [max(lower, min(upper, v)) for v in values]

    def add_fill(x, y_upper, y_lower, color):
        fig.add_trace(
            go.Scatter(
                x=x + x[::-1],
                y=y_upper + y_lower[::-1],
                mode="lines",
                fill="toself",
                fillcolor=color,
                line=dict(color=color, width=0),
                hoverinfo="skip",
                hovertemplate=None,
                showlegend=False,
            )
        )

    # In-range bands
    p10_in_range = clip_to_range(p10, target_lower, target_upper)
    p90_in_range = clip_to_range(p90, target_lower, target_upper)
    add_fill(x_values, p90_in_range, p10_in_range, COLORS["agp"]["in_range_90th"])

    p25_in_range = clip_to_range(p25, target_lower, target_upper)
    p75_in_range = clip_to_range(p75, target_lower, target_upper)
    add_fill(x_values, p75_in_range, p25_in_range, COLORS["agp"]["in_range_75th"])

    # Median line
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p50,
            mode="lines",
            line=dict(color=COLORS["agp"]["in_range_median"], width=3),
            showlegend=False,
            hoverinfo="skip",
            hovertemplate=None,
        )
    )

    # Above-range bands
    p75_above = [max(v, target_upper) for v in p75]
    add_fill(
        x_values,
        p75_above,
        [target_upper] * len(x_values),
        COLORS["agp"]["above_range_75th"],
    )

    p90_above = [max(v, target_upper) for v in p90]
    add_fill(x_values, p90_above, p75_above, COLORS["agp"]["above_range_90th"])

    # Below-range bands
    p25_below = [min(v, target_lower) for v in p25]
    add_fill(
        x_values,
        [target_lower] * len(x_values),
        p25_below,
        COLORS["agp"]["under_range_75th"],
    )

    p10_below = [min(v, target_lower) for v in p10]
    add_fill(x_values, p25_below, p10_below, COLORS["agp"]["under_range_90th"])


def _add_cgm_scatter(
    fig: go.Figure, cgm_data: list, rotation_hours: float, target_range: tuple
):
    """Add CGM scatter points to the figure."""
    if not cgm_data:
        return

    target_lower, target_upper = target_range
    points_per_hour = 12

    day_x = []
    day_y = []
    day_colors = []
    timestamps = []

    for reading in cgm_data:
        original_hour = reading["hour"]
        adjusted_hour = (original_hour - rotation_hours) % 24
        day_x.append(adjusted_hour * points_per_hour)
        day_y.append(reading["value"])
        timestamps.append(reading["timestamp"])

        value = reading["value"]
        if value < target_lower:
            day_colors.append(COLORS["diafit"]["under_range"])
        elif value > target_upper:
            day_colors.append(COLORS["diafit"]["above_range"])
        else:
            day_colors.append(COLORS["diafit"]["in_range"])

    fig.add_trace(
        go.Scatter(
            x=day_x,
            y=day_y,
            mode="markers",
            marker=dict(size=6, color=day_colors, opacity=1.0),
            customdata=timestamps,
            showlegend=False,
            hoverinfo="y",
            hovertemplate="Time: %{customdata}<br>Value: %{y} mg/dL",
        )
    )


def _calculate_tick_positions(time_labels: list) -> tuple:
    """Calculate x-axis tick positions for 3-hour intervals."""
    target_times = [f"{hour:02d}:00" for hour in range(0, 24, 3)]
    tick_vals = []
    tick_texts = []

    for target_time in target_times:
        try:
            target_dt = datetime.strptime(target_time, "%H:%M")
            closest_idx = _find_closest_time_index(
                time_labels, target_dt.hour, target_dt.minute
            )
            tick_vals.append(closest_idx)
            tick_texts.append(target_time)
        except ValueError:
            continue

    return tick_vals, tick_texts


def create_agp_plotly_graph(
    agp_data: dict,
    cgm_data: list = None,
    end_timestamp: str = "00:00",
    extend_hours: int = 0,
) -> str:
    """Generate a Plotly AGP chart and return JSON for embedding.

    Args:
        agp_data: Dictionary containing AGP percentile data (always 0:00-24:00)
        cgm_data: Optional list of dicts with 'hour' and 'value' for CGM readings
        end_timestamp: End time for the AGP window (e.g., "18:00"). Default "00:00".
        extend_hours: Number of hours to extend the graph past end_timestamp.

    Returns:
        JSON string containing the Plotly figure data, layout, and config.
    """
    # Extract and prepare data
    time_labels = agp_data.get("time", [])
    p10 = agp_data.get("p10", [])
    p25 = agp_data.get("p25", [])
    p50 = agp_data.get("p50", [])
    p75 = agp_data.get("p75", [])
    p90 = agp_data.get("p90", [])

    # Rotate data to start/end at specified timestamp
    time_labels, p10, p25, p50, p75, p90, rotation_hours = _rotate_agp_data(
        time_labels, p10, p25, p50, p75, p90, end_timestamp
    )

    # Extend data for additional hours if requested
    time_labels, p10, p25, p50, p75, p90 = _extend_agp_data(
        time_labels, p10, p25, p50, p75, p90, extend_hours
    )

    # Create figure
    fig = go.Figure()
    x_values = list(range(len(time_labels)))
    target_range = (70, 180)

    # Add target range background
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="y",
        x0=0,
        x1=1,
        y0=target_range[0],
        y1=target_range[1],
        fillcolor=COLORS["theme"]["background_tertiary"],
        line=dict(width=0),
        layer="below",
    )

    # Add percentile bands
    _add_percentile_bands(fig, x_values, p10, p25, p50, p75, p90, target_range)

    # Add CGM scatter points
    _add_cgm_scatter(fig, cgm_data, rotation_hours, target_range)

    # Calculate tick positions
    tick_vals, tick_texts = _calculate_tick_positions(time_labels)

    # Configure layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_texts,
            gridcolor="#30363d",
            tickfont=dict(color="#8b949e"),
            range=[0, len(x_values) - 1],
        ),
        yaxis=dict(range=[0, 250], showgrid=False, tickfont=dict(color="#8b949e")),
        hovermode=False,
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        margin=dict(l=2, r=0, t=0, b=0),
        showlegend=False,
        dragmode=False,
    )

    config = {
        "displayModeBar": False,
        "staticPlot": False,
        "editable": False,
        "displaylogo": False,
    }

    return json.dumps(
        {"data": fig.data, "layout": fig.layout, "config": config},
        cls=PlotlyJSONEncoder,
    )
