import json

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder


def create_agp_plotly_graph(agp_data):
    """Generate a Plotly AGP chart and return JSON for embedding."""
    time_labels = agp_data.get("time", [])
    p10 = agp_data.get("p10", [])
    p25 = agp_data.get("p25", [])
    p50 = agp_data.get("p50", [])
    p75 = agp_data.get("p75", [])
    p90 = agp_data.get("p90", [])

    x_values = list(range(len(time_labels)))
    fig = go.Figure()

    # 90th percentile band
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p90,
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            name="90th Percentile",
            showlegend=False,
        )
    )

    # 75th percentile band
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p75,
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(153, 102, 255, 0.2)",
            name="75th-90th Percentile",
            showlegend=False,
        )
    )

    # Median
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p50,
            mode="lines",
            line=dict(color="rgba(75, 192, 192, 1)", width=3),
            name="Median (50th)",
            showlegend=False,
        )
    )

    # IQR (25th-75th)
    fig.add_trace(
        go.Scatter(
            x=x_values + x_values[::-1],
            y=p75 + p25[::-1],
            mode="lines",
            fill="toself",
            fillcolor="rgba(54, 162, 235, 0.3)",
            line=dict(width=0),
            showlegend=False,
            name="25th-75th Percentile (IQR)",
        )
    )

    # 25th percentile band
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p25,
            mode="lines",
            line=dict(color="rgba(54, 162, 235, 0.8)", width=2),
            name="25th Percentile",
            showlegend=False,
        )
    )

    # 10th percentile band
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=p10,
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(153, 102, 255, 0.2)",
            name="10th-25th Percentile",
            showlegend=False,
        )
    )

    # Add reference lines
    for y, color, label in [(70, "orange", "70"), (180, "red", "180")]:
        fig.add_hline(
            y=y,
            line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="right",
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=x_values[::12],
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 12)],
            gridcolor="#30363d",
            tickfont=dict(color="#8b949e"),
        ),
        yaxis=dict(range=[0, 400], gridcolor="#30363d", tickfont=dict(color="#8b949e")),
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
