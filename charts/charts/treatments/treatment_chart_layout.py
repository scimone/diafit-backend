import plotly.graph_objects as go


def get_treatment_chart_layout() -> go.Layout:
    layout = go.Layout(
        yaxis2=dict(
            showgrid=False,
            showticklabels=False,
        ),
        yaxis3=dict(
            showgrid=False,
            showticklabels=False,
        ),
    )
    return layout
