import pandas as pd

from charts.charts import datetime_to_numeric
from diafit_backend.features.cluster_treatments import (
    hierarchical_clustering_treatments,
)


def get_hover_data(logs, agg_data, log_type, unit):
    hover_texts = []
    total_boluses = []

    for idx in range(len(agg_data)):
        total_bolus = agg_data[log_type, "sum"].iloc[idx]
        dates = agg_data["timestamp", "list"].iloc[idx]
        times = [d.strftime("%H:%M") for d in dates]
        boluses = agg_data[log_type, "list"].iloc[idx]

        # Multi-bolus case
        if len(boluses) > 1:
            bolus_list = [f"{t}: {b} {unit}" for t, b in zip(times, boluses)]
            name = (
                f"<b>Total: {round(total_bolus, 1)} {unit}</b>"
                "<br />" + "<br />".join(bolus_list)
            )

        # Single-bolus case
        else:
            ts = logs.timestamp.iloc[idx].strftime("%H:%M")
            b = round(logs[log_type].iloc[idx], 1)
            name = f"<b>{ts}: {b} {unit}</b>"

        hover_texts.append(name)
        total_boluses.append(total_bolus)

    return hover_texts, total_boluses


def get_treatment_chart_data(treatment_data, log_type, start_timestamp, max_value):
    # Convert to DataFrame
    unit = "U" if log_type == "bolus" else "g"
    timestamps = [item["timestamp"] for item in treatment_data]
    values = [item["value"] for item in treatment_data]

    logs = pd.DataFrame(
        {
            "timestamp": timestamps,
            log_type: values,
        }
    )
    len_logs = len(logs)

    agg_data = hierarchical_clustering_treatments(logs, log_type)
    agg_data[("min_time", "")] = agg_data[("min_time", "")].apply(
        lambda x: datetime_to_numeric(x, start_timestamp)
    )

    agg_data[("max_time", "")] = agg_data[("max_time", "")].apply(
        lambda x: datetime_to_numeric(x, start_timestamp)
    )
    hover_data = get_hover_data(logs, agg_data, log_type, unit=unit)

    return {
        "logs": logs,
        "log_type": log_type,
        "len_logs": len_logs,
        "hover_data": hover_data,
        "agg_data": agg_data,
        "max_value": max_value,
    }
