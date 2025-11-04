from datetime import datetime

from ninja import Query, Router

from api.schemas.cgm_schema import CgmInSchema, CgmOutSchema
from diafit_backend.models import CgmEntity

router = Router(tags=["CGM"])


@router.get(
    path="/list",
    response=list[CgmOutSchema],
    tags=["CGM"],
    summary="List CGM Entries",
    description="Retrieve a list of CGM entries.",
)
def list_cgm(
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
    Returns the latest CGM entries, limited by 'count'.
    """
    queryset = CgmEntity.objects.all()

    # Apply timestamp range filters if provided
    if start and end:
        queryset = queryset.filter(timestamp__range=(start, end))
    elif start:
        queryset = queryset.filter(timestamp__gte=start)
    elif end:
        queryset = queryset.filter(timestamp__lte=end)

    queryset = queryset.order_by("-timestamp")[:count]
    return list(queryset)


@router.post(
    path="/create",
    response=CgmOutSchema,
    tags=["CGM"],
    summary="Create CGM Entry",
    description="Create a new CGM entry.",
)
def create_cgm(request, payload: CgmInSchema):
    """
    Creates a new CGM entry.
    """
    cgm_entry = CgmEntity(**payload.dict())
    cgm_entry.save()
    return cgm_entry


@router.post(
    path="/bulk",
    response={201: list[CgmOutSchema]},
    tags=["CGM"],
    summary="Bulk Create CGM Entries",
    description="Insert multiple CGM entries efficiently in one request.",
)
def create_cgm_bulk(request, payload: list[CgmInSchema]):
    """
    Accepts a list of CGM readings and stores them efficiently using bulk_create.
    """
    # Convert payload list into model objects
    cgm_objects = [CgmEntity(**item.dict()) for item in payload]

    # Bulk insert all at once
    created = CgmEntity.objects.bulk_create(cgm_objects)

    return created
