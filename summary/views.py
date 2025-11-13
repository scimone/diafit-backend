import json

import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import render
from plotly.utils import PlotlyJSONEncoder

from .models import RollingSummary


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
    agp_patterns = None

    if summary and summary.agp:
        try:
            plotly_graph = create_agp_plotly_graph(summary.agp)
            # Get patterns from database (already calculated and stored)
            agp_patterns = summary.agp_trends
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
        "agp_patterns": agp_patterns,
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
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            showlegend=False,
        )
    )

    # 75th-90th percentile range (fill) - outer area
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_75,
            name="75th-90th Percentile",
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(153, 102, 255, 0.2)",
            showlegend=False,
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
            showlegend=False,
        )
    )

    # 25th-75th percentile range (IQR - fill) - inner area
    fig.add_trace(
        go.Scatter(
            x=x_values + x_values[::-1],
            y=percentile_75 + percentile_25[::-1],
            name="25th-75th Percentile (IQR)",
            mode="lines",
            line=dict(color="rgba(54, 162, 235, 0)", width=0),
            fill="toself",
            fillcolor="rgba(54, 162, 235, 0.3)",
            showlegend=False,
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
            showlegend=False,
        )
    )

    # 10th-25th percentile range (fill) - outer area
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=percentile_10,
            name="10th-25th Percentile",
            mode="lines",
            line=dict(color="rgba(153, 102, 255, 0.8)", width=2),
            fill="tonexty",
            fillcolor="rgba(153, 102, 255, 0.2)",
            showlegend=False,
        )
    )

    # Add target range reference lines
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="orange",
        annotation_text="70",
        annotation_position="right",
    )
    fig.add_hline(
        y=180,
        line_dash="dash",
        line_color="red",
        annotation_text="180",
        annotation_position="right",
    )

    # Update layout
    fig.update_layout(
        xaxis=dict(
            # title=dict(text="Time of Day", font=dict(color="#8b949e")),
            tickmode="array",
            tickvals=x_values[::12]
            if len(x_values) > 12
            else x_values,  # Show every 12th tick
            ticktext=[time_labels[i] for i in range(0, len(time_labels), 12)]
            if len(time_labels) > 12
            else time_labels,
            tickfont=dict(color="#8b949e"),
            gridcolor="#30363d",
        ),
        yaxis=dict(
            # title=dict(text="Glucose (mg/dL)", font=dict(color="#8b949e")),
            range=[0, 400],
            tickfont=dict(color="#8b949e"),
            gridcolor="#30363d",
        ),
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        height=400,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),  # Reduce margins: left, right, top, bottom
    )

    # Convert to JSON for embedding
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json


def agp_data_api(request):
    """
    API endpoint to get AGP data as JSON for a specific date and period_days.
    """
    user = request.user
    period_days = int(request.GET.get("period_days", 14))

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
        "period_days": summary.period_days,
        "agp": summary.agp or {},
        "agp_summary": summary.agp_summary,
        "glucose_avg": summary.glucose_avg,
        "time_in_range": summary.time_in_range,
        "time_below_range": summary.time_below_range,
        "time_above_range": summary.time_above_range,
    }

    return JsonResponse(response_data)
