import plotly.graph_objects as go

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_cgm_chart_traces(cgm_chart_data: dict):
    """Generate Plotly traces for CGM scatter points."""
    # Create scatter trace for CGM data points
    scatter_trace = go.Scatter(
        x=cgm_chart_data["day_x"],
        y=cgm_chart_data["day_y"],
        mode="markers",
        name="CGM",
        marker=dict(size=6, color=cgm_chart_data["day_colors"], opacity=1.0),
        customdata=cgm_chart_data["timestamps"],
        showlegend=False,
        hoverinfo="y",
        hovertemplate="Time: %{customdata}<br>Value: %{y} mg/dL",
    )

    return [scatter_trace]
