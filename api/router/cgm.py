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
def list_cgm(request, count: int = Query(10, description="Number of entries to fetch")):
    """
    Returns the latest CGM entries, limited by 'count'.
    """
    queryset = CgmEntity.objects.order_by("-timestamp")[:count]
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
