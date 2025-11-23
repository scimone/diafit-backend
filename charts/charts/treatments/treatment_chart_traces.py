from datetime import timedelta

import plotly.graph_objects as go

from core.colors import COLORS


def get_treatment_chart_traces(treatment_chart_data: dict):
    # def plot_treatments(logs, log_type, unit, max_value):
    logs = treatment_chart_data["logs"]
    log_type = treatment_chart_data["log_type"]
    agg_data = treatment_chart_data["agg_data"]
    hover_texts, total_boluses = treatment_chart_data["hover_data"]
    max_value = treatment_chart_data["max_value"]

    traces = []
    if len(logs) > 1:  # multiple entries on that day
        for i in range(len(agg_data)):
            traces.append(
                go.Scatter(
                    x=[
                        agg_data.min_time.iloc[i],
                        agg_data.max_time.iloc[i],
                        agg_data.max_time.iloc[i],
                        agg_data.min_time.iloc[i],
                    ],
                    y=[-0.5, -0.5, 0.5, 0.5],
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
        traces.append(
            go.Scatter(
                x=[min_time, max_time, max_time, min_time],
                y=[0, 0, 1, 1],
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
