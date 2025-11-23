import plotly.graph_objects as go

from charts.charts.agp import get_agp_chart_layout

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_home_chart_layout(range) -> go.Layout:
    """Generate Plotly layout for Home chart."""

    layout = get_agp_chart_layout()
    layout.update(
        hovermode="closest",
        spikedistance=-1,
    )
    layout.yaxis.update(zeroline=False)
    layout.xaxis.update(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="#30363d",
        spikethickness=3,
        range=range,
    )
    return layout
