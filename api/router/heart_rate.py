from datetime import datetime
from typing import List

from ninja import Query, Router

from api.schemas.hr_schema import HeartRateInSchema, HeartRateOutSchema
from diafit_backend.models import HeartRateEntity

router = Router(tags=["Heart Rate"])


@router.post(
    path="/create",
    response=HeartRateOutSchema,
    summary="Create Heart Rate Entry",
    description="Create a new heart rate measurement entry.",
)
def create_heart_rate(request, payload: HeartRateInSchema):
    """
    Create a heart rate entry.
    """
    heart_rate = HeartRateEntity(**payload.dict())
    heart_rate.save()
    return heart_rate


@router.get(
    path="/list",
    response=List[HeartRateOutSchema],
    summary="List Heart Rate Entries",
    description="Retrieve latest heart rate entries, optionally filtered by timestamp range, limited by count.",
)
def list_heart_rate(
    request,
    count: int = Query(10, description="Maximum number of results to return"),
    start: datetime | None = Query(
        None, description="Filter from this timestamp (UTC, ISO8601)"
    ),
    end: datetime | None = Query(
        None, description="Filter up to this timestamp (UTC, ISO8601)"
    ),
):
    """
    Example usage:
    - /api/heart_rate/list?count=5
    - /api/heart_rate/list?start=2025-11-03T00:00:00Z&end=2025-11-03T23:59:59Z
    """
    queryset = HeartRateEntity.objects.all()

    # Apply timestamp range filters if provided
    if start and end:
        queryset = queryset.filter(timestamp__range=(start, end))
    elif start:
        queryset = queryset.filter(timestamp__gte=start)
    elif end:
        queryset = queryset.filter(timestamp__lte=end)

    # Order and limit results
    queryset = queryset.order_by("-timestamp")[:count]

    return list(queryset)


@router.get(
    path="/{source_id}",
    response=HeartRateOutSchema,
    summary="Get Heart Rate Entry",
    description="Retrieve a specific heart rate entry by source ID.",
)
def get_heart_rate(request, source_id: str):
    """
    Get a single heart rate entry by source ID.
    """
    try:
        heart_rate = HeartRateEntity.objects.get(source_id=source_id)
    except HeartRateEntity.DoesNotExist:
        return 404, {"message": "Heart rate entry not found"}

    return heart_rate


@router.delete(
    path="/{heart_rate_id}",
    response={204: None},
    summary="Delete Heart Rate Entry",
    description="Delete a heart rate entry by ID.",
)
def delete_heart_rate(request, heart_rate_id: int):
    """
    Delete a heart rate entry.
    """
    try:
        heart_rate = HeartRateEntity.objects.get(id=heart_rate_id)
        heart_rate.delete()
        return 204, None
    except HeartRateEntity.DoesNotExist:
        return 404, {"message": "Heart rate entry not found"}
