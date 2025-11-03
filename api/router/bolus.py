from typing import List

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
    description="Retrieve latest bolus entries, limited by count.",
)
def list_bolus(request, count: int = Query(10)):
    queryset = BolusEntity.objects.order_by("-timestamp_utc")[:count]
    return list(queryset)
