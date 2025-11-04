from datetime import datetime
from typing import List, Optional

from ninja import Query, Router

from api.schemas.meal_schema import MealInSchema, MealOutSchema
from diafit_backend.models import MealEntity

router = Router(tags=["Meal"])


@router.post(
    path="/create",
    response=MealOutSchema,
    summary="Create Meal Entry",
    description="Create a new meal entry.",
)
def create_meal(request, payload: MealInSchema):
    meal = MealEntity(**payload.dict())
    meal.save()
    return meal


@router.post(
    path="/bulk",
    response={201: str},
    summary="Bulk Insert Meal Entries",
    description="Insert multiple meal entries efficiently.",
)
def bulk_create_meal(request, payloads: List[MealInSchema]):
    entries = [MealEntity(**p.dict()) for p in payloads]
    MealEntity.objects.bulk_create(entries, ignore_conflicts=True)
    return 201, f"Inserted {len(entries)} meal records."


@router.get(
    path="/list",
    response=List[MealOutSchema],
    summary="List Meal Entries",
    description="Retrieve latest meal entries, optionally filtered by timestamp range, meal type, or impact type, limited by count.",
)
def list_meal(
    request,
    count: int = Query(10, description="Maximum number of results to return"),
    start: datetime | None = Query(
        None, description="Filter from this timestamp (UTC, ISO8601)"
    ),
    end: datetime | None = Query(
        None, description="Filter up to this timestamp (UTC, ISO8601)"
    ),
    meal_type: Optional[str] = Query(
        None,
        description="Filter by meal type (e.g. 'BREAKFAST', 'LUNCH', 'DINNER', 'SNACK')",
    ),
    impact_type: Optional[str] = Query(
        None,
        description="Filter by impact type (e.g. 'SHORT', 'MEDIUM', 'LONG')",
    ),
):
    """
    Example usage:
    - /api/meal/list?count=5
    - /api/meal/list?start=2025-11-03T00:00:00Z&end=2025-11-03T23:59:59Z
    - /api/meal/list?meal_type=BREAKFAST
    - /api/meal/list?impact_type=LONG
    """
    queryset = MealEntity.objects.all()

    # Apply timestamp range filters if provided
    if start and end:
        queryset = queryset.filter(meal_time_utc__range=(start, end))
    elif start:
        queryset = queryset.filter(meal_time_utc__gte=start)
    elif end:
        queryset = queryset.filter(meal_time_utc__lte=end)

    # Apply optional filters
    if meal_type:
        queryset = queryset.filter(meal_type__iexact=meal_type)
    if impact_type:
        queryset = queryset.filter(impact_type__iexact=impact_type)

    # Order and limit results
    queryset = queryset.order_by("-meal_time_utc")[:count]

    return list(queryset)
