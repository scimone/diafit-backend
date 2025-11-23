from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone
from pytz import UTC
from pytz import timezone as pytz_timezone

from charts.charts.home.home_chart import get_home_chart
from diafit_backend.models.bolus_entity import BolusEntity
from diafit_backend.models.cgm_entity import CgmEntity
from diafit_backend.models.meal_entity import MealEntity
from summary.services import get_agp_summary


@login_required
def home_view(request):
    user = request.user

    if not user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this resource.")

    period_days = int(request.GET.get("period_days", 14))

    # Define time range for today's data
    hours = 24
    extend_hours = 3
    end_timestamp = timezone.now().astimezone(UTC)
    start_timestamp = end_timestamp - timezone.timedelta(hours=hours)
    user_tz = pytz_timezone(user.settings.timezone) if user.settings.timezone else UTC

    # Get AGP data
    summary = get_agp_summary(user, period_days)
    agp_patterns = summary.agp_trends
    agp_data = summary.agp if summary and summary.agp else None

    # Get CGM data
    cgm_data = (
        CgmEntity.objects.filter(
            user=user, timestamp__gte=start_timestamp, timestamp__lte=end_timestamp
        )
        .order_by("timestamp")
        .values_list("timestamp", "value_mgdl")
    )
    cgm_data = [
        {"timestamp": ts.astimezone(user_tz), "value": val} for ts, val in cgm_data
    ]

    # Get bolus data
    bolus_data = (
        BolusEntity.objects.filter(
            user=user,
            timestamp_utc__gte=start_timestamp,
            timestamp_utc__lte=end_timestamp,
        )
        .order_by("timestamp_utc")
        .values_list("timestamp_utc", "value")
    )
    bolus_data = [
        {"timestamp": ts.astimezone(user_tz), "value": val} for ts, val in bolus_data
    ]

    # Get carb data
    carb_data = (
        MealEntity.objects.filter(
            user=user,
            meal_time_utc__gte=start_timestamp,
            meal_time_utc__lte=end_timestamp,
        )
        .order_by("meal_time_utc")
        .values_list("meal_time_utc", "carbohydrates")
    )
    carb_data = [
        {"timestamp": ts.astimezone(user_tz), "value": val} for ts, val in carb_data
    ]

    fig_home = get_home_chart(
        hours=hours,
        extend_hours=extend_hours,
        x_axis_range=(
            start_timestamp.astimezone(user_tz),
            end_timestamp.astimezone(user_tz),
        ),
        agp_data=agp_data,
        cgm_data=cgm_data,
        bolus_data=bolus_data,
        carb_data=carb_data,
    )

    # Generate error_message if needed
    error_message = None
    if not cgm_data:
        error_message = "No CGM data available for the selected period."
    elif not bolus_data:
        error_message = "No bolus data available for the selected period."
    elif not agp_data:
        error_message = "No AGP summary data available for the selected period."

    context = {
        "summary": summary,
        "plotly_graph": fig_home,
        "error_message": error_message,
        "period_days": period_days,
        "available_periods": [1, 3, 7, 14, 30, 90],
        "agp_patterns": agp_patterns,
    }
    return render(request, "home.html", context)
