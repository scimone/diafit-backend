import numpy as np
import pandas as pd

from charts.charts import datetime_to_numeric
from diafit_backend.features.cluster_treatments import (
    hierarchical_clustering_treatments,
)


def generate_rounded_rect_coords(
    x_min, x_max, y_min, y_max, radius=0.15, num_points=10
):
    """
    Generate x, y coordinates for a rounded rectangle.

    Parameters:
        x_min, x_max: horizontal bounds
        y_min, y_max: vertical bounds
        radius: corner radius (in y-axis units)
        num_points: number of points per corner arc

    Returns:
        x_coords, y_coords: lists of coordinates forming a closed rounded rectangle
    """
    x_coords = []
    y_coords = []

    # Clamp radius to not exceed half the height
    actual_radius = min(radius, (y_max - y_min) / 2)

    # Bottom-left corner (counterclockwise from bottom-right of arc)
    theta = np.linspace(np.pi, 3 * np.pi / 2, num_points)
    x_coords.extend((x_min + actual_radius) + actual_radius * np.cos(theta))
    y_coords.extend((y_min + actual_radius) + actual_radius * np.sin(theta))

    # Bottom-right corner
    theta = np.linspace(3 * np.pi / 2, 2 * np.pi, num_points)
    x_coords.extend((x_max - actual_radius) + actual_radius * np.cos(theta))
    y_coords.extend((y_min + actual_radius) + actual_radius * np.sin(theta))

    # Top-right corner
    theta = np.linspace(0, np.pi / 2, num_points)
    x_coords.extend((x_max - actual_radius) + actual_radius * np.cos(theta))
    y_coords.extend((y_max - actual_radius) + actual_radius * np.sin(theta))

    # Top-left corner
    theta = np.linspace(np.pi / 2, np.pi, num_points)
    x_coords.extend((x_min + actual_radius) + actual_radius * np.cos(theta))
    y_coords.extend((y_max - actual_radius) + actual_radius * np.sin(theta))

    # Close the shape
    x_coords.append(x_coords[0])
    y_coords.append(y_coords[0])

    return x_coords, y_coords


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

    # Calculate rounded rectangle coordinates for each treatment cluster
    rounded_coords = []
    for idx in range(len(agg_data)):
        x_min = agg_data[("min_time", "")].iloc[idx]
        x_max = agg_data[("max_time", "")].iloc[idx]
        x_coords, y_coords = generate_rounded_rect_coords(
            x_min, x_max, y_min=-0.35, y_max=0.35, radius=0.3
        )
        rounded_coords.append({"x": x_coords, "y": y_coords})

    return {
        "logs": logs,
        "log_type": log_type,
        "len_logs": len_logs,
        "hover_data": hover_data,
        "agg_data": agg_data,
        "max_value": max_value,
        "rounded_coords": rounded_coords,
    }
