import plotly.graph_objects as go


def get_base_layout() -> go.Layout:
    """Generate base Plotly layout for charts."""
    layout = go.Layout(
        hovermode=False,
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        showlegend=False,
        dragmode=False,
    )
    return layout


def get_base_config() -> dict:
    """Generate base Plotly config for charts."""
    config = {
        "displayModeBar": False,
        "staticPlot": False,
        "editable": False,
        "displaylogo": False,
    }

    return config
