import plotly.graph_objects as go


def get_sleep_chart_layout() -> go.Layout:
    layout = go.Layout(
        yaxis2=dict(
            showgrid=False,
            showticklabels=False,
            range=[-0.5, 0.5],
        ),
    )
    return layout
