# summary/views/agp_views.py
from django.shortcuts import render

from summary.services import create_agp_plotly_graph, get_agp_summary


def agp_visualization(request):
    user = request.user
    period_days = int(request.GET.get("period_days", 14))

    summary = get_agp_summary(user, period_days)
    plotly_graph, error_message, agp_patterns = None, None, None

    if summary and summary.agp:
        try:
            plotly_graph = create_agp_plotly_graph(summary.agp)
            agp_patterns = summary.agp_trends
        except Exception as e:
            error_message = f"Error creating graph: {e}"
    else:
        error_message = (
            f"No AGP data available for {period_days}-day rolling summaries."
        )

    context = {
        "summary": summary,
        "plotly_graph": plotly_graph,
        "error_message": error_message,
        "period_days": period_days,
        "available_periods": [7, 14, 30, 90],
        "agp_patterns": agp_patterns,
    }
    return render(request, "summary/agp_visualization.html", context)
