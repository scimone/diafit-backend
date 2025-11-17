# summary/views/agp_views.py
from datetime import datetime, time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone
from pytz import UTC
from pytz import timezone as pytz_timezone

from diafit_backend.models.cgm_entity import CgmEntity
from summary.services import create_agp_plotly_graph, get_agp_summary


@login_required
def agp_visualization(request):
    user = request.user

    if not user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this resource.")

    period_days = int(request.GET.get("period_days", 14))

    summary = get_agp_summary(user, period_days)
    plotly_graph, error_message, agp_patterns = None, None, None

    # Get today's CGM data (from midnight until now)
    now = timezone.now()
    tz = pytz_timezone("Europe/Berlin")
    now_tz = timezone.localtime(now, tz)
    today_start_tz = tz.localize(datetime.combine(now_tz.date(), time.min))
    today_start_utc = today_start_tz.astimezone(UTC)
    now_utc = now_tz.astimezone(UTC)
    today_cgm_data = (
        CgmEntity.objects.filter(
            user=user, timestamp__gte=today_start_utc, timestamp__lte=now_utc
        )
        .order_by("timestamp")
        .values_list("timestamp", "value_mgdl")
    )

    # Convert to format suitable for plotting
    today_cgm = [
        {
            "timestamp": timezone.localtime(ts, tz).strftime("%H:%M:%S"),
            "hour": timezone.localtime(ts, tz).hour
            + timezone.localtime(ts, tz).minute / 60.0,
            "value": val,
        }
        for ts, val in today_cgm_data
    ]

    if summary and summary.agp:
        try:
            plotly_graph = create_agp_plotly_graph(summary.agp, today_cgm)
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
        "available_periods": [1, 3, 7, 14, 30, 90],
        "agp_patterns": agp_patterns,
    }
    return render(request, "summary/agp_visualization.html", context)
