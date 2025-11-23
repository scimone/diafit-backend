from charts.charts.agp import (
    get_agp_chart_data,
)
from charts.charts.cgm import get_cgm_chart_data
from charts.charts.treatments import get_treatment_chart_data


def get_home_chart_data(
    agp_data: dict,
    cgm_data: dict,
    bolus_data: dict,
    carb_data: dict,
    start_timestamp,
    end_timestamp,
    extend_hours: int,
) -> dict:
    agp_chart_data = get_agp_chart_data(
        agp_data,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        extend_hours=extend_hours,
    )

    cgm_chart_data = get_cgm_chart_data(
        cgm_data=cgm_data, start_timestamp=start_timestamp
    )

    bolus_chart_data = get_treatment_chart_data(
        treatment_data=bolus_data,
        log_type="bolus",
        start_timestamp=start_timestamp,
        max_value=10,
    )

    carb_chart_data = get_treatment_chart_data(
        treatment_data=carb_data,
        log_type="carbs",
        start_timestamp=start_timestamp,
        max_value=100,
    )

    return {
        "agp_chart_data": agp_chart_data,
        "cgm_chart_data": cgm_chart_data,
        "bolus_chart_data": bolus_chart_data,
        "carb_chart_data": carb_chart_data,
    }
