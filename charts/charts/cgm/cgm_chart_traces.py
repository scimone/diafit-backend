import pandas as pd
import plotly.graph_objects as go

# TODO: Get from user settings
TARGET_RANGE = (70, 180)
TIMEZONE = "Europe/Berlin"


def get_customdata_structured(timestamps):
    now = pd.Timestamp.now(tz=TIMEZONE)
    today = now.normalize()
    yesterday = today - pd.Timedelta(days=1)

    dates = pd.Series(timestamps).dt.normalize()
    times = pd.Series(timestamps).dt.strftime("%H:%M")

    def format_date(date):
        if date == today:
            return "Today"
        elif date == yesterday:
            return "Yesterday"
        else:
            return date.strftime("%d.%m.%Y")

    formatted_dates = dates.apply(format_date)
    return pd.DataFrame({"date": formatted_dates, "time": times}).to_numpy()


def get_cgm_chart_traces(cgm_chart_data: dict):
    """Generate Plotly traces for CGM scatter points."""
    # Create scatter trace for CGM data points
    scatter_trace = go.Scatter(
        x=cgm_chart_data["day_x"],
        y=cgm_chart_data["day_y"],
        mode="markers",
        name="CGM",
        marker=dict(size=6, color=cgm_chart_data["day_colors"], opacity=1.0),
        customdata=get_customdata_structured(cgm_chart_data["timestamps"]),
        showlegend=False,
        hoverinfo="y",
        hovertemplate="%{customdata[0]}, %{customdata[1]}<br><b>%{y} mg/dL</b>",
    )

    return [scatter_trace]
