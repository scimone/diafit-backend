from datetime import datetime
from typing import List, Optional

from ninja import Query, Router

from api.schemas.bolus_schema import BolusInSchema, BolusOutSchema
from diafit_backend.models import BolusEntity

router = Router(tags=["Bolus"])


@router.post(
    path="/create",
    response=BolusOutSchema,
    summary="Create Bolus Entry",
    description="Create a new insulin bolus entry.",
)
def create_bolus(request, payload: BolusInSchema):
    bolus = BolusEntity(**payload.dict())
    bolus.save()
    return bolus


@router.post(
    path="/bulk",
    response={201: str},
    summary="Bulk Insert Bolus Entries",
    description="Insert multiple bolus entries efficiently.",
)
def bulk_create_bolus(request, payloads: List[BolusInSchema]):
    entries = [BolusEntity(**p.dict()) for p in payloads]
    BolusEntity.objects.bulk_create(entries, ignore_conflicts=True)
    return 201, f"Inserted {len(entries)} bolus records."


@router.get(
    path="/list",
    response=List[BolusOutSchema],
    summary="List Bolus Entries",
    description="Retrieve latest bolus entries, optionally filtered by timestamp range, limited by count.",
)
def list_bolus(
    request,
    count: int = Query(10, description="Maximum number of results to return"),
    start: datetime | None = Query(
        None, description="Filter from this timestamp (UTC, ISO8601)"
    ),
    end: datetime | None = Query(
        None, description="Filter up to this timestamp (UTC, ISO8601)"
    ),
    event_type: Optional[str] = Query(
        None,
        description="Filter by event type (e.g. 'Correction Bolus', 'Meal Bolus', etc.)",
    ),
):
    """
    Example usage:
    - /api/bolus/list?count=5
    - /api/bolus/list?start=2025-11-03T00:00:00Z&end=2025-11-03T23:59:59Z
    """
    queryset = BolusEntity.objects.all()

    # Apply timestamp range filters if provided
    if start and end:
        queryset = queryset.filter(timestamp_utc__range=(start, end))
    elif start:
        queryset = queryset.filter(timestamp_utc__gte=start)
    elif end:
        queryset = queryset.filter(timestamp_utc__lte=end)

    # Apply event type filter if provided
    if event_type:
        queryset = queryset.filter(event_type__iexact=event_type)

    # Order and limit results
    queryset = queryset.order_by("-timestamp_utc")[:count]

    return list(queryset)
