# summary/services/agp_plot.py
import json

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from diafit_backend.config.colors import COLOR_SCHEMES


def create_agp_plotly_graph(agp_data: dict) -> str:
    """Generate a Plotly AGP chart and return JSON for embedding."""
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
                line=dict(color=color),
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
    for y, color, label in [(70, "grey", "70"), (180, "grey", "180")]:
        fig.add_hline(
            y=y,
            # line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="left",
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=x_values[::24],
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 24)],
            gridcolor="#30363d",
            tickfont=dict(color="#8b949e"),
        ),
        yaxis=dict(range=[0, 400], gridcolor="#30363d", tickfont=dict(color="#8b949e")),
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
