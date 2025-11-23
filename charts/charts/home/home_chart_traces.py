from charts.charts.agp import (
    get_agp_chart_traces,
)
from charts.charts.cgm import get_cgm_chart_traces
from charts.charts.sleep.sleep_chart_traces import get_sleep_chart_traces
from charts.charts.treatments import get_treatment_chart_traces


def get_home_chart_traces(
    agp_chart_data: dict,
    cgm_chart_data: dict,
    sleep_chart_data: dict,
    bolus_chart_data: dict,
    carb_chart_data: dict,
):
    # agp
    agp_traces = get_agp_chart_traces(agp_chart_data)

    # cgm
    cgm_traces = get_cgm_chart_traces(cgm_chart_data)

    # sleep
    sleep_traces = get_sleep_chart_traces(sleep_chart_data)

    # bolus
    bolus_traces = get_treatment_chart_traces(bolus_chart_data)

    # carbs
    carb_traces = get_treatment_chart_traces(carb_chart_data)

    return {
        "agp_traces": agp_traces,
        "cgm_traces": cgm_traces,
        "bolus_traces": bolus_traces,
        "carb_traces": carb_traces,
        "sleep_traces": sleep_traces,
    }
