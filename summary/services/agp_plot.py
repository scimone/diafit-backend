# summary/services/agp_plot.py
import json

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from diafit_backend.config.colors import COLOR_SCHEMES


def create_agp_plotly_graph(agp_data: dict, today_cgm: list = None) -> str:
    """Generate a Plotly AGP chart and return JSON for embedding.

    Args:
        agp_data: Dictionary containing AGP percentile data
        today_cgm: Optional list of dicts with 'hour' and 'value' for today's CGM readings
    """
    time_labels = agp_data.get("time", [])
    p10 = agp_data.get("p10", [])
    p25 = agp_data.get("p25", [])
    p50 = agp_data.get("p50", [])
    p75 = agp_data.get("p75", [])
    p90 = agp_data.get("p90", [])

    x_values = list(range(len(time_labels)))
    fig = go.Figure()

    # Target range bounds
    TARGET_RANGE = (70, 180)
    target_lower, target_upper = TARGET_RANGE

    # Helper to clip values to target range
    def clip_to_range(values, lower, upper):
        return [max(lower, min(upper, v)) for v in values]

    # Helper to add percentile fill area
    def add_percentile_fill(fig, x, y_upper, y_lower, color):
        fig.add_trace(
            go.Scatter(
                x=x + x[::-1],
                y=y_upper + y_lower[::-1],
                mode="lines",
                fill="toself",
                fillcolor=color,
                line=dict(color=color, width=0),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # 10-90th percentile in range (light green)
    p10_in_range = clip_to_range(p10, target_lower, target_upper)
    p90_in_range = clip_to_range(p90, target_lower, target_upper)
    add_percentile_fill(
        fig, x_values, p90_in_range, p10_in_range, COLOR_SCHEMES["agp"]["in_range_90th"]
    )

    # 25-75th percentile in range (dark green)
    p25_in_range = clip_to_range(p25, target_lower, target_upper)
    p75_in_range = clip_to_range(p75, target_lower, target_upper)
    add_percentile_fill(
        fig, x_values, p75_in_range, p25_in_range, COLOR_SCHEMES["agp"]["in_range_75th"]
    )

    # Median
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p50,
            mode="lines",
            line=dict(color=COLOR_SCHEMES["agp"]["in_range_median"], width=3),
            name="Median (50th)",
            showlegend=False,
        )
    )

    # 25-75th percentile above range (dark purple)
    p75_above = [max(v, target_upper) for v in p75]
    add_percentile_fill(
        fig,
        x_values,
        p75_above,
        [target_upper] * len(x_values),
        COLOR_SCHEMES["agp"]["above_range_75th"],
    )

    # 25-75th percentile below range (dark red)
    p25_below = [min(v, target_lower) for v in p25]
    add_percentile_fill(
        fig,
        x_values,
        [target_lower] * len(x_values),
        p25_below,
        COLOR_SCHEMES["agp"]["under_range_75th"],
    )

    # 10-90th percentile above range (light purple)
    p90_above = [max(v, target_upper) for v in p90]
    add_percentile_fill(
        fig, x_values, p90_above, p75_above, COLOR_SCHEMES["agp"]["above_range_90th"]
    )

    # 10-90th percentile below range (light red)
    p10_below = [min(v, target_lower) for v in p10]
    add_percentile_fill(
        fig, x_values, p25_below, p10_below, COLOR_SCHEMES["agp"]["under_range_90th"]
    )

    # Add reference lines
    for y, color, label in [
        (target_lower, COLOR_SCHEMES["diafit"]["under_range"], "70"),
        (target_upper, COLOR_SCHEMES["diafit"]["above_range"], "180"),
    ]:
        fig.add_hline(
            y=y,
            # line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="left",
        )

    # Add today's CGM scatter points if available
    if today_cgm:
        # Convert hours to x-axis indices (assuming 12 points per hour)
        points_per_hour = 12
        today_x = [reading["hour"] * points_per_hour for reading in today_cgm]
        today_y = [reading["value"] for reading in today_cgm]

        # Assign colors based on target range
        today_colors = []
        for reading in today_cgm:
            value = reading["value"]
            if value < target_lower:
                today_colors.append(COLOR_SCHEMES["diafit"]["under_range"])
            elif value > target_upper:
                today_colors.append(COLOR_SCHEMES["diafit"]["above_range"])
            else:
                today_colors.append(COLOR_SCHEMES["diafit"]["in_range"])

        fig.add_trace(
            go.Scatter(
                x=today_x,
                y=today_y,
                mode="markers",
                marker=dict(
                    size=6,
                    color=today_colors,
                    opacity=1.0,
                    line=dict(width=0.5, color="#0d1117"),
                ),
                name="Today's CGM",
                hovertemplate="<b>Today</b><br>Time: %{customdata}<br>Glucose: %{y} mg/dL<extra></extra>",
                customdata=[reading["timestamp"] for reading in today_cgm],
                showlegend=False,
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=x_values[::24],
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 24)],
            gridcolor="#30363d",
            tickfont=dict(color="#8b949e"),
        ),
        yaxis=dict(range=[0, 300], gridcolor="#30363d", tickfont=dict(color="#8b949e")),
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
