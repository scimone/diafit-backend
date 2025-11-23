import json
from datetime import timedelta

from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder

from charts.charts import get_base_config
from charts.charts.home.home_chart_data import get_home_chart_data
from charts.charts.home.home_chart_layout import (
    get_home_chart_layout,
    get_home_chart_xaxis,
)
from charts.charts.home.home_chart_traces import get_home_chart_traces
from charts.charts.treatments.treatment_chart_layout import get_treatment_chart_layout


def get_home_chart(
    extend_hours: int,
    x_axis_range: tuple,
    agp_data,
    cgm_data,
    sleep_data,
    bolus_data,
    carb_data,
):
    start_timestamp, end_timestamp = x_axis_range
    home_chart_data = get_home_chart_data(
        agp_data,
        cgm_data,
        sleep_data,
        bolus_data,
        carb_data,
        start_timestamp,
        end_timestamp,
        extend_hours,
    )
    home_chart_traces = get_home_chart_traces(
        home_chart_data["agp_chart_data"],
        home_chart_data["cgm_chart_data"],
        home_chart_data["sleep_chart_data"],
        home_chart_data["bolus_chart_data"],
        home_chart_data["carb_chart_data"],
    )

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.1, 0.1, 0.1],
        vertical_spacing=0,
    )

    for trace in home_chart_traces["agp_traces"]:
        fig.add_trace(trace, row=1, col=1)

    for trace in home_chart_traces["cgm_traces"]:
        fig.add_trace(trace, row=1, col=1)

    for trace in home_chart_traces["sleep_traces"]:
        fig.add_trace(trace, row=2, col=1)

    for trace in home_chart_traces["bolus_traces"]:
        fig.add_trace(trace, row=3, col=1)

    for trace in home_chart_traces["carb_traces"]:
        fig.add_trace(trace, row=4, col=1)

    # Layout updates
    home_layout = get_home_chart_layout()
    treatment_layout = get_treatment_chart_layout()
    fig.update_layout(home_layout)
    fig.update_layout(treatment_layout)
    fig.update_traces(xaxis="x4")
    fig.update_layout(
        xaxis4=get_home_chart_xaxis(
            start_timestamp, end_timestamp + timedelta(hours=extend_hours)
        ),
    )

    config = get_base_config()

    return json.dumps(
        {"data": fig.data, "layout": fig.layout, "config": config},
        cls=PlotlyJSONEncoder,
    )
