import json

import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from plotly.utils import PlotlyJSONEncoder

from .models import RollingSummary


@login_required
def agp_visualization(request):
    """
    Render AGP visualization page with dropdown to select period_days and date from rolling summaries.
    """
    user = request.user

    # Get selected period_days and date from query parameters
    period_days = int(request.GET.get("period_days", 14))  # Default to 14 days

    # Get the selected summary (or latest if none selected)
    try:
        summary = RollingSummary.objects.get(
            user=user,
            period_days=period_days,
            # agp__isnull=False,
        )
    except RollingSummary.DoesNotExist:
        summary = None

    # Generate Plotly graph if summary exists
    plotly_graph = None
    error_message = None

    if summary and summary.agp:
        try:
            plotly_graph = create_agp_plotly_graph(summary.agp)
        except Exception as e:
            error_message = f"Error creating graph: {str(e)}"
            print(error_message)
    elif not summary:
        error_message = f"No AGP data available for {period_days}-day rolling summaries. Please ensure rolling summaries are calculated."

    context = {
        "summary": summary,
        "plotly_graph": plotly_graph,
        "error_message": error_message,
        "period_days": period_days,
        "available_periods": [7, 14, 30, 90],
    }

    return render(request, "summary/agp_visualization.html", context)


def create_agp_plotly_graph(agp_data):
    """
    Create a Plotly graph object from AGP data.
    Returns JSON string for embedding in template.

    AGP data format:
    {
      "p10": [80, 82, 85, ...],
      "p25": [90, 92, 95, ...],
      "p50": [100, 102, 104, ...],
      "p75": [110, 112, 115, ...],
      "p90": [120, 125, 130, ...],
      "time": ["00:00", "00:05", "00:10", ...]
    }
    """
    # Extract data from AGP structure
    time_labels = agp_data.get("time", [])
    percentile_10 = agp_data.get("p10", [])
    percentile_25 = agp_data.get("p25", [])
    percentile_50 = agp_data.get("p50", [])
    percentile_75 = agp_data.get("p75", [])
    percentile_90 = agp_data.get("p90", [])

    # Use indices for x-axis
    x_values = list(range(len(time_labels)))

    # Create the figure
    fig = go.Figure()

    # Add percentile traces with filled areas
    # 90th percentile (upper bound)
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_90,
            name="90th Percentile",
            mode="lines",
            line=dict(color="rgba(255, 99, 132, 0.8)", width=2),
            showlegend=True,
        )
    )

    # 75th-90th percentile range (fill)
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_75,
            name="75th-90th Percentile",
            mode="lines",
            line=dict(color="rgba(255, 159, 64, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(255, 159, 64, 0.2)",
            showlegend=True,
        )
    )

    # Median (50th percentile)
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_50,
            name="Median (50th)",
            mode="lines",
            line=dict(color="rgba(75, 192, 192, 1)", width=3),
            showlegend=True,
        )
    )

    # 25th-75th percentile range (IQR - fill)
    fig.add_trace(
        go.Scatter(
            x=x_values + x_values[::-1],
            y=percentile_75 + percentile_25[::-1],
            name="25th-75th Percentile (IQR)",
            mode="lines",
            line=dict(color="rgba(54, 162, 235, 0)", width=0),
            fill="toself",
            fillcolor="rgba(54, 162, 235, 0.3)",
            showlegend=True,
        )
    )

    # 25th percentile
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_25,
            name="25th Percentile",
            mode="lines",
            line=dict(color="rgba(54, 162, 235, 0.8)", width=2),
            showlegend=True,
        )
    )

    # 10th-25th percentile range (fill)
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_10,
            name="10th-25th Percentile",
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(153, 102, 255, 0.2)",
            showlegend=True,
        )
    )

    # Add target range reference lines
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="orange",
        annotation_text="Low threshold (70 mg/dL)",
        annotation_position="right",
    )
    fig.add_hline(
        y=180,
        line_dash="dash",
        line_color="red",
        annotation_text="High threshold (180 mg/dL)",
        annotation_position="right",
    )

    # Update layout
    fig.update_layout(
        title={
            "text": "24-Hour Ambulatory Glucose Profile (AGP)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20},
        },
        xaxis=dict(
            title="Time of Day",
            tickmode="array",
            tickvals=x_values[::12]
            if len(x_values) > 12
            else x_values,  # Show every 12th tick
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 12)]
            if len(time_labels) > 12
            else time_labels,
            gridcolor="rgba(200, 200, 200, 0.3)",
        ),
        yaxis=dict(
            title="Glucose (mg/dL)",
            range=[0, 400],
            gridcolor="rgba(200, 200, 200, 0.3)",
        ),
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    # Convert to JSON for embedding
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json


@login_required
def agp_data_api(request):
    """
    API endpoint to get AGP data as JSON for a specific date and period_days.
    """
    user = request.user
    selected_date = request.GET.get("date")
    period_days = int(request.GET.get("period_days", 14))

    if selected_date:
        try:
            summary = RollingSummary.objects.get(
                user=user,
                date=selected_date,
                period_days=period_days,
                agp__isnull=False,
            )
        except RollingSummary.DoesNotExist:
            return JsonResponse(
                {"error": "No data found for this date and period"}, status=404
            )
    else:
        summary = (
            RollingSummary.objects.filter(
                user=user, period_days=period_days, agp__isnull=False
            )
            .order_by("-date")
            .first()
        )
        if not summary:
            return JsonResponse({"error": "No AGP data available"}, status=404)

    response_data = {
        "date": summary.date,
        "period_days": summary.period_days,
        "agp": summary.agp or {},
        "agp_summary": summary.agp_summary,
        "glucose_avg": summary.glucose_avg,
        "time_in_range": summary.time_in_range,
        "time_below_range": summary.time_below_range,
        "time_above_range": summary.time_above_range,
    }

    return JsonResponse(response_data)
