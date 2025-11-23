import plotly.graph_objects as go


def get_treatment_chart_layout() -> go.Layout:
    layout = go.Layout(
        yaxis3=dict(
            showgrid=False,
            showticklabels=False,
        ),
        yaxis4=dict(
            showgrid=False,
            showticklabels=False,
        ),
    )
    return layout
