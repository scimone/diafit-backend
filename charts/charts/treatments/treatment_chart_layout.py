import plotly.graph_objects as go


def get_treatment_chart_layout() -> go.Layout:
    layout = go.Layout(
        yaxis3=dict(
            showgrid=False,
            showticklabels=False,
            range=[-0.5, 0.5],
            fixedrange=True,
        ),
        yaxis4=dict(
            showgrid=False,
            showticklabels=False,
            range=[-0.5, 0.5],
            fixedrange=True,
        ),
    )
    return layout
