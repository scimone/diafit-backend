import pandas as pd
from scipy.cluster.hierarchy import fcluster, ward


def hierarchical_clustering_treatments(logs_today, log_type, max_d=1.5):
    logs_today["time"] = (
        logs_today.timestamp.dt.hour
        + logs_today.timestamp.dt.minute / 60
        + logs_today.timestamp.dt.second / (60 * 60)
    )
    data = logs_today.time.to_numpy()
    nnumbers = data.reshape(-1)
    data = data.reshape(-1, 1)
    Z = ward(data)
    color = fcluster(Z, t=max_d, criterion="distance")
    grouped_item = pd.DataFrame(
        list(zip(nnumbers, color, logs_today[log_type], logs_today.timestamp)),
        columns=["numbers", "segment", log_type, "timestamp"],
    ).groupby("segment")
    agg_data = grouped_item.agg(
        {log_type: ["sum", "list"], "timestamp": ["min", "max", "list"]}
    )
    agg_data = agg_data.reset_index()
    agg_data["timedelta"] = agg_data.timestamp["max"] - agg_data.timestamp["min"]

    agg_data["middle_time"] = agg_data.timestamp["min"] + agg_data["timedelta"] / 2
    agg_data["min_time"] = agg_data["middle_time"] - pd.Timedelta(minutes=30)
    agg_data["max_time"] = agg_data["middle_time"] + pd.Timedelta(minutes=30)
    return agg_data
