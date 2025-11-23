import plotly.graph_objects as go

from charts.charts.base import get_base_layout
from charts.charts.target_range import get_target_range_chart

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_agp_chart_layout() -> go.Layout:
    """Generate Plotly layout for AGP chart."""
    # tick_vals, tick_texts = calculate_tick_positions(agp_chart_data["time_labels"])

    layout = get_base_layout()
    layout.update(
        margin=dict(l=2, r=0, t=0, b=0),
        shapes=[get_target_range_chart()],
    )

    layout.xaxis.update(
        tickmode="array",
        # tickvals=tick_vals,
        # ticktext=tick_texts,
        gridcolor="#30363d",
        tickfont=dict(color="#8b949e"),
        # range=[0, len(agp_chart_data["x_values"]) - 1],  # Use x_values length
        zeroline=True,
    )
    layout.yaxis.update(
        range=[0, 250],
        tickvals=[TARGET_RANGE[0], TARGET_RANGE[1]],
        showgrid=False,
        tickfont=dict(color="#8b949e"),
        zeroline=True,
    )

    return go.Layout(layout)
