# api/router/summary.py

from datetime import datetime
from typing import List, Optional

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
    date: Optional[datetime] = Query(None, description="Specific date (YYYY-MM-DD)"),
    start_date: Optional[datetime] = Query(
        None, description="Date range start (YYYY-MM-DD)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Date range end (YYYY-MM-DD)"
    ),
):
    """
    Example usage:
    - /api/summary/daily?user_id=1&count=5
    - /api/summary/daily?user_id=1&date=2024-01-15
    - /api/summary/daily?user_id=1&start_date=2024-01-01&end_date=2024-01-31
    """
    queryset = DailySummary.objects.filter(user_id=user_id)

    # Apply date filtering
    if date:
        queryset = queryset.filter(date=date.date())
    elif start_date and end_date:
        queryset = queryset.filter(date__range=[start_date.date(), end_date.date()])
    elif start_date:
        queryset = queryset.filter(date__gte=start_date.date())
    elif end_date:
        queryset = queryset.filter(date__lte=end_date.date())

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
    count: int = Query(10, description="Maximum number of results to return"),
    year: Optional[int] = Query(None, description="Specific year"),
    week: Optional[int] = Query(None, description="Specific week number (1-53)"),
    start_year: Optional[int] = Query(None, description="Year range start"),
    end_year: Optional[int] = Query(None, description="Year range end"),
):
    """
    Example usage:
    - /api/summary/weekly?user_id=1&count=5
    - /api/summary/weekly?user_id=1&year=2024&week=15
    - /api/summary/weekly?user_id=1&start_year=2023&end_year=2024
    """
    queryset = WeeklySummary.objects.filter(user_id=user_id)

    # Apply filtering
    if year:
        queryset = queryset.filter(year=year)
    if week:
        queryset = queryset.filter(week=week)
    if start_year and end_year:
        queryset = queryset.filter(year__range=[start_year, end_year])
    elif start_year:
        queryset = queryset.filter(year__gte=start_year)
    elif end_year:
        queryset = queryset.filter(year__lte=end_year)

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
    count: int = Query(10, description="Maximum number of results to return"),
    year: Optional[int] = Query(None, description="Specific year"),
    month: Optional[int] = Query(None, description="Specific month (1-12)"),
    start_year: Optional[int] = Query(None, description="Year range start"),
    end_year: Optional[int] = Query(None, description="Year range end"),
):
    """
    Example usage:
    - /api/summary/monthly?user_id=1&count=5
    - /api/summary/monthly?user_id=1&year=2024&month=3
    - /api/summary/monthly?user_id=1&start_year=2023&end_year=2024
    """
    queryset = MonthlySummary.objects.filter(user_id=user_id)

    # Apply filtering
    if year:
        queryset = queryset.filter(year=year)
    if month:
        queryset = queryset.filter(month=month)
    if start_year and end_year:
        queryset = queryset.filter(year__range=[start_year, end_year])
    elif start_year:
        queryset = queryset.filter(year__gte=start_year)
    elif end_year:
        queryset = queryset.filter(year__lte=end_year)

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
    count: int = Query(10, description="Maximum number of results to return"),
    year: Optional[int] = Query(None, description="Specific year"),
    quarter: Optional[int] = Query(None, description="Specific quarter (1-4)"),
    start_year: Optional[int] = Query(None, description="Year range start"),
    end_year: Optional[int] = Query(None, description="Year range end"),
):
    """
    Example usage:
    - /api/summary/quarterly?user_id=1&count=5
    - /api/summary/quarterly?user_id=1&year=2024&quarter=1
    - /api/summary/quarterly?user_id=1&start_year=2023&end_year=2024
    """
    queryset = QuarterlySummary.objects.filter(user_id=user_id)

    # Apply filtering
    if year:
        queryset = queryset.filter(year=year)
    if quarter:
        queryset = queryset.filter(quarter=quarter)
    if start_year and end_year:
        queryset = queryset.filter(year__range=[start_year, end_year])
    elif start_year:
        queryset = queryset.filter(year__gte=start_year)
    elif end_year:
        queryset = queryset.filter(year__lte=end_year)

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
        None, description="Rolling period (1, 3, 7, 14, 30, 90)"
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
