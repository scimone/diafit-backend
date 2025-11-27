from datetime import timedelta

import plotly.graph_objects as go

from charts.charts.treatments.treatment_chart_data import generate_rounded_rect_coords
from core.colors import COLORS


def get_treatment_chart_traces(treatment_chart_data: dict):
    # def plot_treatments(logs, log_type, unit, max_value):
    logs = treatment_chart_data["logs"]
    log_type = treatment_chart_data["log_type"]
    agg_data = treatment_chart_data["agg_data"]
    hover_texts, total_boluses = treatment_chart_data["hover_data"]
    rounded_coords = treatment_chart_data["rounded_coords"]
    max_value = treatment_chart_data["max_value"]

    traces = []
    if len(logs) > 1:  # multiple entries on that day
        for i in range(len(agg_data)):
            traces.append(
                go.Scatter(
                    x=rounded_coords[i]["x"],
                    y=rounded_coords[i]["y"],
                    fill="toself",
                    hoveron="fills",
                    hoverlabel=dict(font_size=9),
                    hoverinfo="text",
                    name=hover_texts[i],
                    line=dict(color="rgba(0,0,0,0)"),
                    fillcolor=COLORS["diafit"][log_type],
                    opacity=min(total_boluses[i] / max_value, 1),
                ),
            )
    else:  # only 1 entry on that day
        min_time = logs.timestamp.iloc[0] - timedelta(minutes=30)
        max_time = logs.timestamp.iloc[0] + timedelta(minutes=30)
        x_coords, y_coords = generate_rounded_rect_coords(
            min_time, max_time, y_min=0, y_max=1, radius=0.15
        )
        traces.append(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                fill="toself",
                hoveron="fills",
                hoverinfo="text",
                hoverlabel=dict(font_size=10),
                name=hover_texts[0],
                line=dict(color="rgba(0,0,0,0)"),
                fillcolor=COLORS["diafit"][log_type],
                opacity=min(total_boluses[0] / max_value, 1),
            ),
        )
    return traces
