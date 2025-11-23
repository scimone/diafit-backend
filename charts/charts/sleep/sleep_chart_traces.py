import plotly.graph_objs as go

from core.colors import COLORS


def get_sleep_chart_traces(sleep_chart_data: dict):
    y_level = 0  # fixed y position for badges
    traces = []

    for x_start, x_end in zip(
        sleep_chart_data["sleep_start_x"], sleep_chart_data["sleep_end_x"]
    ):
        traces.append(
            go.Scatter(
                x=[x_start, x_end],
                y=[y_level, y_level],
                mode="lines+markers",
                line=dict(width=6, dash="solid"),  # the colored line
                marker=dict(
                    size=12,
                    symbol="triangle-up",  # start marker
                    color=COLORS["diafit"]["sleep"],
                ),
                showlegend=False,
            )
        )

        # end marker (separate trace so symbol differs)
        traces.append(
            go.Scatter(
                x=[x_end],
                y=[y_level],
                mode="markers",
                marker=dict(
                    size=12,
                    symbol="triangle-down",  # end marker
                    color="blue",
                ),
                showlegend=False,
            )
        )
    return traces
