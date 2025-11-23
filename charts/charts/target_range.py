import plotly.graph_objects as go

from core.colors import COLORS

target_range = (70, 180)  # TODO: fetch from user settings


def get_target_range_chart():
    rect = go.layout.Shape(
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

    return rect
