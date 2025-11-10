from datetime import datetime
from typing import List

from ninja import Query, Router

from api.schemas.sleep_schema import (
    SleepSessionInSchema,
    SleepSessionOutSchema,
    SleepStageOutSchema,
)
from diafit_backend.models import SleepSessionEntity, SleepStageEntity

router = Router(tags=["Sleep"])


@router.post(
    path="/create",
    response=SleepSessionOutSchema,
    summary="Create Sleep Session",
    description="Create a new sleep session with optional stages.",
)
def create_sleep_session(request, payload: SleepSessionInSchema):
    """
    Create a sleep session. If stages are provided, they will be created as well.
    """
    stages_data = payload.stages
    payload_dict = payload.dict(exclude={"stages"})

    session = SleepSessionEntity(**payload_dict)
    session.save()

    # Create stages if provided
    if stages_data:
        for stage_data in stages_data:
            stage = SleepStageEntity(session=session, **stage_data.dict())
            stage.save()  # This will auto-calculate duration_minutes

        # Recalculate stage-specific durations
        session.calculate_stage_durations()

    # Return session with stages
    return SleepSessionOutSchema(
        **{
            **session.__dict__,
            "stages": [
                SleepStageOutSchema(**stage.__dict__) for stage in session.stages.all()
            ]
            if stages_data
            else None,
        }
    )


@router.get(
    path="/list",
    response=List[SleepSessionOutSchema],
    summary="List Sleep Sessions",
    description="Retrieve latest sleep sessions, optionally filtered by date range, limited by count.",
)
def list_sleep_sessions(
    request,
    count: int = Query(10, description="Maximum number of results to return"),
    start: datetime | None = Query(
        None, description="Filter from this timestamp (UTC, ISO8601)"
    ),
    end: datetime | None = Query(
        None, description="Filter up to this timestamp (UTC, ISO8601)"
    ),
    include_stages: bool = Query(False, description="Include sleep stages in response"),
):
    """
    Example usage:
    - /api/sleep/list?count=5
    - /api/sleep/list?start=2025-11-03T00:00:00Z&end=2025-11-03T23:59:59Z
    - /api/sleep/list?count=10&include_stages=true
    """
    queryset = SleepSessionEntity.objects.all()

    # Apply timestamp range filters if provided
    if start and end:
        queryset = queryset.filter(start_time__range=(start, end))
    elif start:
        queryset = queryset.filter(start_time__gte=start)
    elif end:
        queryset = queryset.filter(start_time__lte=end)

    # Order and limit results
    queryset = queryset.order_by("-start_time")[:count]

    # Prefetch stages if requested
    if include_stages:
        queryset = queryset.prefetch_related("stages")

    # Build response
    results = []
    for session in queryset:
        session_dict = session.__dict__
        if include_stages:
            session_dict["stages"] = [
                SleepStageOutSchema(**stage.__dict__) for stage in session.stages.all()
            ]
        else:
            session_dict["stages"] = None
        results.append(SleepSessionOutSchema(**session_dict))

    return results


@router.get(
    path="/{source_id}",
    response=SleepSessionOutSchema,
    summary="Get Sleep Session",
    description="Retrieve a specific sleep session by ID with all its stages.",
)
def get_sleep_session(
    request,
    source_id: str,
    include_stages: bool = Query(True, description="Include sleep stages in response"),
):
    """
    Get a single sleep session with all its stages.
    """
    try:
        if include_stages:
            session = SleepSessionEntity.objects.prefetch_related("stages").get(
                source_id=source_id
            )
        else:
            session = SleepSessionEntity.objects.get(source_id=source_id)
    except SleepSessionEntity.DoesNotExist:
        return 404, {"message": "Sleep session not found"}

    return SleepSessionOutSchema(
        **{
            **session.__dict__,
            "stages": [
                SleepStageOutSchema(**stage.__dict__) for stage in session.stages.all()
            ]
            if include_stages
            else None,
        }
    )


@router.get(
    path="/stats/summary",
    response=dict,
    summary="Get Sleep Statistics",
    description="Get aggregated sleep statistics for a time period.",
)
def get_sleep_stats(
    request,
    start: datetime = Query(..., description="Start date (UTC, ISO8601)"),
    end: datetime = Query(..., description="End date (UTC, ISO8601)"),
):
    """
    Get sleep statistics including average duration, sleep stage breakdown, etc.

    Example usage:
    - /api/sleep/stats/summary?start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z
    """
    sessions = SleepSessionEntity.objects.filter(start_time__range=(start, end))

    if not sessions.exists():
        return {
            "total_sessions": 0,
            "average_duration_minutes": 0,
            "average_deep_sleep_minutes": 0,
            "average_light_sleep_minutes": 0,
            "average_rem_sleep_minutes": 0,
            "average_awake_minutes": 0,
        }

    total = sessions.count()

    return {
        "total_sessions": total,
        "average_duration_minutes": sum(s.total_duration_minutes or 0 for s in sessions)
        / total,
        "average_deep_sleep_minutes": sum(s.deep_sleep_minutes or 0 for s in sessions)
        / total,
        "average_light_sleep_minutes": sum(s.light_sleep_minutes or 0 for s in sessions)
        / total,
        "average_rem_sleep_minutes": sum(s.rem_sleep_minutes or 0 for s in sessions)
        / total,
        "average_awake_minutes": sum(s.awake_minutes or 0 for s in sessions) / total,
    }


@router.delete(
    path="/{session_id}",
    response={204: None},
    summary="Delete Sleep Session",
    description="Delete a sleep session and all its associated stages.",
)
def delete_sleep_session(request, session_id: int):
    """
    Delete a sleep session. Stages will be automatically deleted due to CASCADE.
    """
    try:
        session = SleepSessionEntity.objects.get(id=session_id)
        session.delete()
        return 204, None
    except SleepSessionEntity.DoesNotExist:
        return 404, {"message": "Sleep session not found"}
