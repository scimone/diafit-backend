import plotly.graph_objects as go

from charts.charts.agp import get_agp_chart_layout
from charts.charts.util import calculate_tick_positions, datetime_to_numeric

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_home_chart_xaxis(start_timestamp, end_timestamp):
    tick_vals, tick_texts = calculate_tick_positions(
        start_timestamp,
        end_timestamp,
        interval_hours=3,
    )
    return dict(
        gridcolor="#30363d",
        tickfont=dict(color="#8b949e"),
        showticklabels=True,
        showline=False,
        showgrid=True,
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_texts,
        range=[0, datetime_to_numeric(end_timestamp, start_timestamp)],
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="#30363d",
        spikethickness=3,
    )


def get_home_chart_layout() -> go.Layout:
    """Generate Plotly layout for Home chart."""

    layout = get_agp_chart_layout()
    layout.update(
        hovermode="closest",
        spikedistance=-1,
    )
    layout.yaxis.update(zeroline=False)
    return layout
