import json
from datetime import datetime

from plotly.utils import PlotlyJSONEncoder

from charts.charts.agp.agp_chart_data import get_agp_chart_data
from charts.charts.agp.agp_chart_layout import get_agp_chart_layout
from charts.charts.agp.agp_chart_traces import get_agp_chart_traces
from charts.charts.base import get_base_config


def get_agp_chart(
    agp_data: dict,
    start_timestamp: datetime = datetime.strptime("00:00", "%H:%M"),
    end_timestamp: datetime = datetime.strptime("00:00", "%H:%M"),
    extend_hours: int = 0,
) -> str:
    """Generate a Plotly AGP chart and return JSON for embedding.

    Args:
        agp_chart_data: Dictionary containing AGP percentile data (always 0:00-24:00)

    Returns:
        JSON string containing the Plotly figure data, layout, and config.
    """

    chart_data = get_agp_chart_data(
        agp_data, start_timestamp, end_timestamp, extend_hours
    )
    traces = get_agp_chart_traces(chart_data)
    layout = get_agp_chart_layout()
    config = get_base_config()

    return json.dumps(
        {"data": traces, "layout": layout, "config": config},
        cls=PlotlyJSONEncoder,
    )
