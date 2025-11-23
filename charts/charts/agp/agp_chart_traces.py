import plotly.graph_objects as go

from core.colors import COLORS

TARGET_RANGE = (70, 180)  # TODO: Get from user settings


def get_agp_chart_traces(
    agp_chart_data: dict,
):
    """Generate Plotly traces for AGP percentile bands."""
    target_lower, target_upper = TARGET_RANGE

    def clip_to_range(values, lower, upper):
        return [max(lower, min(upper, v)) for v in values]

    def get_fill_trace(name, x, y_upper, y_lower, color):
        trace = go.Scatter(
            x=x + x[::-1],
            y=y_upper + y_lower[::-1],
            mode="lines",
            fill="toself",
            fillcolor=color,
            line=dict(color=color, width=0),
            hoverinfo="skip",
            hovertemplate=None,
            showlegend=False,
            name=name,
        )
        return trace

    # Create traces
    traces = []
    x_values = agp_chart_data["x_values"]  # Use indices instead of time_labels

    # In-range 90th band
    p10_in_range = clip_to_range(agp_chart_data["p10"], target_lower, target_upper)
    p90_in_range = clip_to_range(agp_chart_data["p90"], target_lower, target_upper)
    traces.append(
        get_fill_trace(
            "In Range 90th",
            x_values,
            p90_in_range,
            p10_in_range,
            COLORS["agp"]["in_range_90th"],
        )
    )

    # In-range 75th band
    p25_in_range = clip_to_range(agp_chart_data["p25"], target_lower, target_upper)
    p75_in_range = clip_to_range(agp_chart_data["p75"], target_lower, target_upper)
    traces.append(
        get_fill_trace(
            "In Range 75th",
            x_values,
            p75_in_range,
            p25_in_range,
            COLORS["agp"]["in_range_75th"],
        )
    )

    # Median line
    traces.append(
        go.Scatter(
            x=x_values,
            y=agp_chart_data["p50"],
            mode="lines",
            line=dict(color=COLORS["agp"]["in_range_median"], width=3),
            showlegend=False,
            hoverinfo="skip",
            hovertemplate=None,
            name="Median",
        )
    )

    # Above-range 75th band
    p75_above = [max(v, target_upper) for v in agp_chart_data["p75"]]
    traces.append(
        get_fill_trace(
            "Above Range 75th",
            x_values,
            p75_above,
            [target_upper] * len(x_values),
            COLORS["agp"]["above_range_75th"],
        )
    )

    # Above-range 90th band
    p90_above = [max(v, target_upper) for v in agp_chart_data["p90"]]
    traces.append(
        get_fill_trace(
            "Above Range 90th",
            x_values,
            p90_above,
            p75_above,
            COLORS["agp"]["above_range_90th"],
        )
    )

    # Below-range 25th band
    p25_below = [min(v, target_lower) for v in agp_chart_data["p25"]]
    traces.append(
        get_fill_trace(
            "Below Range 25th",
            x_values,
            [target_lower] * len(x_values),
            p25_below,
            COLORS["agp"]["under_range_75th"],
        )
    )

    # Below-range 10th band
    p10_below = [min(v, target_lower) for v in agp_chart_data["p10"]]
    traces.append(
        get_fill_trace(
            "Below Range 10th",
            x_values,
            p25_below,
            p10_below,
            COLORS["agp"]["under_range_90th"],
        )
    )

    return traces
