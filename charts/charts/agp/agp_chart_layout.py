from datetime import datetime, timedelta

import plotly.graph_objects as go

from charts.charts.base import get_base_layout
from charts.charts.target_range import get_target_range_chart
from charts.charts.util import calculate_tick_positions, datetime_to_numeric

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_agp_chart_layout(
    start_timestamp: datetime = datetime.strptime("00:00", "%H:%M"),
    end_timestamp: datetime = datetime.strptime("00:00", "%H:%M") + timedelta(days=1),
) -> go.Layout:
    """Generate Plotly layout for AGP chart."""
    tick_vals, tick_texts = calculate_tick_positions(
        start_timestamp,
        end_timestamp,
        interval_hours=3,
    )

    layout = get_base_layout()
    layout.update(
        margin=dict(l=2, r=0, t=0, b=0),
        shapes=[get_target_range_chart()],
    )

    layout.xaxis.update(
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_texts,
        range=[0, datetime_to_numeric(end_timestamp, start_timestamp)],
        gridcolor="#30363d",
        tickfont=dict(color="#8b949e"),
        zeroline=True,
    )
    layout.yaxis.update(
        range=[0, 250],
        tickvals=[TARGET_RANGE[0], TARGET_RANGE[1]],
        showgrid=False,
        tickfont=dict(color="#8b949e"),
        zeroline=True,
        side="left",
        anchor="free",
        position=1,
    )

    return go.Layout(layout)
