# api/router/summary.py

from datetime import datetime
from typing import List, Optional

from django.db import models
from ninja import Query, Router

from api.schemas.summary_schema import (
    DailySummaryOutSchema,
    MonthlySummaryOutSchema,
    QuarterlySummaryOutSchema,
    RollingSummaryOutSchema,
    WeeklySummaryOutSchema,
)
from summary.models import (
    DailySummary,
    MonthlySummary,
    QuarterlySummary,
    RollingSummary,
    WeeklySummary,
)

router = Router(tags=["Summary"])


@router.get(
    path="/daily",
    response=List[DailySummaryOutSchema],
    summary="List Daily Summaries",
    description="Retrieve daily summaries, optionally filtered by date range.",
)
def list_daily_summaries(
    request,
    user_id: int = Query(..., description="User ID"),
    count: int = Query(10, description="Maximum number of results to return"),
    start: Optional[datetime] = Query(
        None, description="Date range start (YYYY-MM-DD)"
    ),
    end: Optional[datetime] = Query(None, description="Date range end (YYYY-MM-DD)"),
):
    """
    Example usage:
    - /api/summary/daily?user_id=1&count=5
    - /api/summary/daily?user_id=1&start=2024-01-01&end=2024-01-31
    """
    queryset = DailySummary.objects.filter(user_id=user_id)

    # Apply date filtering
    if start and end:
        queryset = queryset.filter(date__range=[start.date(), end.date()])
    elif start:
        queryset = queryset.filter(date__gte=start.date())
    elif end:
        queryset = queryset.filter(date__lte=end.date())

    # Order and limit results
    queryset = queryset.order_by("-date")[:count]

    return list(queryset)


@router.get(
    path="/weekly",
    response=List[WeeklySummaryOutSchema],
    summary="List Weekly Summaries",
    description="Retrieve weekly summaries, optionally filtered by year/week.",
)
def list_weekly_summaries(
    request,
    user_id: int = Query(..., description="User ID"),
    start: Optional[str] = Query(None, description="Week range start, e.g., 2024-15"),
    end: Optional[str] = Query(None, description="Week range end, e.g., 2024-15"),
    count: int = Query(10, description="Maximum number of results to return"),
):
    """
    Example usage:
    - /api/summary/weekly?user_id=1&count=5
    - /api/summary/weekly?user_id=1&start=2024-10&end=2024-15
    """
    queryset = WeeklySummary.objects.filter(user_id=user_id)

    # Apply filtering - parse year and week from start/end (format: YYYY-WW)
    if start and end:
        start_year, start_week = int(start.split("-")[0]), int(start.split("-")[1])
        end_year, end_week = int(end.split("-")[0]), int(end.split("-")[1])
        queryset = (
            queryset.filter(year__gte=start_year, year__lte=end_year)
            .filter(
                models.Q(year__gt=start_year)
                | models.Q(year=start_year, week__gte=start_week)
            )
            .filter(
                models.Q(year__lt=end_year)
                | models.Q(year=end_year, week__lte=end_week)
            )
        )
    elif start:
        start_year, start_week = int(start.split("-")[0]), int(start.split("-")[1])
        queryset = queryset.filter(
            models.Q(year__gt=start_year)
            | models.Q(year=start_year, week__gte=start_week)
        )
    elif end:
        end_year, end_week = int(end.split("-")[0]), int(end.split("-")[1])
        queryset = queryset.filter(
            models.Q(year__lt=end_year) | models.Q(year=end_year, week__lte=end_week)
        )

    # Order and limit results
    queryset = queryset.order_by("-year", "-week")[:count]

    return list(queryset)


@router.get(
    path="/monthly",
    response=List[MonthlySummaryOutSchema],
    summary="List Monthly Summaries",
    description="Retrieve monthly summaries, optionally filtered by year/month.",
)
def list_monthly_summaries(
    request,
    user_id: int = Query(..., description="User ID"),
    start: Optional[str] = Query(None, description="Month range start, e.g., 2024-01"),
    end: Optional[str] = Query(None, description="Month range end, e.g., 2024-12"),
    count: int = Query(10, description="Maximum number of results to return"),
):
    """
    Example usage:
    - /api/summary/monthly?user_id=1&count=5
    - /api/summary/monthly?user_id=1&start=2023-01&end=2024-12
    """
    queryset = MonthlySummary.objects.filter(user_id=user_id)

    # Apply filtering - parse year and month from format "YYYY-MM"
    if start and end:
        start_year, start_month = int(start.split("-")[0]), int(start.split("-")[1])
        end_year, end_month = int(end.split("-")[0]), int(end.split("-")[1])
        queryset = (
            queryset.filter(year__gte=start_year, year__lte=end_year)
            .filter(
                models.Q(year__gt=start_year)
                | models.Q(year=start_year, month__gte=start_month)
            )
            .filter(
                models.Q(year__lt=end_year)
                | models.Q(year=end_year, month__lte=end_month)
            )
        )
    elif start:
        start_year, start_month = int(start.split("-")[0]), int(start.split("-")[1])
        queryset = queryset.filter(
            models.Q(year__gt=start_year)
            | models.Q(year=start_year, month__gte=start_month)
        )
    elif end:
        end_year, end_month = int(end.split("-")[0]), int(end.split("-")[1])
        queryset = queryset.filter(
            models.Q(year__lt=end_year) | models.Q(year=end_year, month__lte=end_month)
        )

    # Order and limit results
    queryset = queryset.order_by("-year", "-month")[:count]

    return list(queryset)


@router.get(
    path="/quarterly",
    response=List[QuarterlySummaryOutSchema],
    summary="List Quarterly Summaries",
    description="Retrieve quarterly summaries, optionally filtered by year/quarter.",
)
def list_quarterly_summaries(
    request,
    user_id: int = Query(..., description="User ID"),
    start: Optional[str] = Query(
        None, description="Quarter range start, e.g., 2024-q1"
    ),
    end: Optional[str] = Query(None, description="Quarter range end, e.g., 2024-q4"),
    count: int = Query(10, description="Maximum number of results to return"),
):
    """
    Example usage:
    - /api/summary/quarterly?user_id=1&count=5
    - /api/summary/quarterly?user_id=1&start=2024-q1&end=2024-q4
    """
    queryset = QuarterlySummary.objects.filter(user_id=user_id)

    # Apply filtering - parse year and quarter from format "YYYY-qQQ"
    if start and end:
        start_year, start_quarter = int(start.split("-q")[0]), int(start.split("-q")[1])
        end_year, end_quarter = int(end.split("-q")[0]), int(end.split("-q")[1])

        queryset = (
            queryset.filter(year__gte=start_year, year__lte=end_year)
            .filter(
                models.Q(year__gt=start_year)
                | models.Q(year=start_year, quarter__gte=start_quarter)
            )
            .filter(
                models.Q(year__lt=end_year)
                | models.Q(year=end_year, quarter__lte=end_quarter)
            )
        )
    elif start:
        start_year, start_quarter = int(start.split("-q")[0]), int(start.split("-q")[1])
        queryset = queryset.filter(
            models.Q(year__gt=start_year)
            | models.Q(year=start_year, quarter__gte=start_quarter)
        )
    elif end:
        end_year, end_quarter = int(end.split("-q")[0]), int(end.split("-q")[1])
        queryset = queryset.filter(
            models.Q(year__lt=end_year)
            | models.Q(year=end_year, quarter__lte=end_quarter)
        )

    # Order and limit results
    queryset = queryset.order_by("-year", "-quarter")[:count]

    return list(queryset)


@router.get(
    path="/rolling",
    response=List[RollingSummaryOutSchema],
    summary="List Rolling Summaries",
    description="Retrieve rolling summaries, optionally filtered by period and date range.",
)
def list_rolling_summaries(
    request,
    user_id: int = Query(..., description="User ID"),
    count: int = Query(10, description="Maximum number of results to return"),
    period_days: Optional[int] = Query(
        None, description="Rolling period (choose between 1, 3, 7, 14, 30, 90)"
    ),
):
    """
    Example usage:
    - /api/summary/rolling?user_id=1&period_days=7
    - /api/summary/rolling?user_id=1&period_days=30&count=1
    """
    queryset = RollingSummary.objects.filter(user_id=user_id)

    # Apply filtering
    if period_days:
        queryset = queryset.filter(period_days=period_days)

    # Order and limit results
    queryset = queryset.order_by("-end_date", "period_days")[:count]

    return list(queryset)
