# summary/services/agp_plot.py
import json

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from core.colors import COLORS


def create_agp_plotly_graph(agp_data: dict, cgm_data: list = None) -> str:
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
                hovertemplate=None,
                showlegend=False,
            )
        )

    # 10-90th percentile in range (light green)
    p10_in_range = clip_to_range(p10, target_lower, target_upper)
    p90_in_range = clip_to_range(p90, target_lower, target_upper)
    add_percentile_fill(
        fig, x_values, p90_in_range, p10_in_range, COLORS["agp"]["in_range_90th"]
    )

    # 25-75th percentile in range (dark green)
    p25_in_range = clip_to_range(p25, target_lower, target_upper)
    p75_in_range = clip_to_range(p75, target_lower, target_upper)
    add_percentile_fill(
        fig, x_values, p75_in_range, p25_in_range, COLORS["agp"]["in_range_75th"]
    )

    # Median
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p50,
            mode="lines",
            line=dict(color=COLORS["agp"]["in_range_median"], width=3),
            name="Median (50th)",
            showlegend=False,
            hoverinfo="skip",
            hovertemplate=None,
        )
    )

    # 25-75th percentile above range (dark purple)
    p75_above = [max(v, target_upper) for v in p75]
    add_percentile_fill(
        fig,
        x_values,
        p75_above,
        [target_upper] * len(x_values),
        COLORS["agp"]["above_range_75th"],
    )

    # 25-75th percentile below range (dark red)
    p25_below = [min(v, target_lower) for v in p25]
    add_percentile_fill(
        fig,
        x_values,
        [target_lower] * len(x_values),
        p25_below,
        COLORS["agp"]["under_range_75th"],
    )

    # 10-90th percentile above range (light purple)
    p90_above = [max(v, target_upper) for v in p90]
    add_percentile_fill(
        fig, x_values, p90_above, p75_above, COLORS["agp"]["above_range_90th"]
    )

    # 10-90th percentile below range (light red)
    p10_below = [min(v, target_lower) for v in p10]
    add_percentile_fill(
        fig, x_values, p25_below, p10_below, COLORS["agp"]["under_range_90th"]
    )

    # Add reference lines
    for y, color, label in [
        (target_lower, COLORS["agp"]["target_lower_line"], "70"),
        (target_upper, COLORS["agp"]["target_upper_line"], "180"),
    ]:
        fig.add_hline(
            y=y,
            # line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="left",
        )

    # Add CGM scatter points if available
    if cgm_data:
        # Convert hours to x-axis indices (assuming 12 points per hour)
        points_per_hour = 12
        day_x = [reading["hour"] * points_per_hour for reading in cgm_data]
        day_y = [reading["value"] for reading in cgm_data]

        # Assign colors based on target range
        day_colors = []
        for reading in cgm_data:
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
                marker=dict(
                    size=6,
                    color=day_colors,
                    opacity=1.0,
                ),
                name="CGM",
                customdata=[reading["timestamp"] for reading in cgm_data],
                showlegend=False,
                hoverinfo="y",  # Enable hover info for today's CGM
                hovertemplate="Time: %{customdata}<br>Value: %{y} mg/dL",  # Custom hover template
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=x_values[::24],
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 24)],
            gridcolor="#30363d",
            tickfont=dict(color="#8b949e"),
            range=[0, len(x_values) - 1],
        ),
        yaxis=dict(range=[0, 250], gridcolor="#30363d", tickfont=dict(color="#8b949e")),
        hovermode=False,
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        margin=dict(l=2, r=0, t=0, b=0),
        showlegend=False,
        dragmode=False,
    )

    # Configure to remove all interactive elements
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
