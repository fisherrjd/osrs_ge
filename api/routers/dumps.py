from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select

from api.db.item_data import engine
from api.schemas.dump_event import DumpEvent

router = APIRouter(
    prefix="/dumps",
    tags=["dumps"],
)


def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session


@router.get("")
def get_dumps(
    session: Annotated[Session, Depends(get_session)],
    # Pagination
    skip: Annotated[int, Query(ge=0, description="Number of events to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max events to return")] = 25,
    # Filters
    event_type: Annotated[
        str | None,
        Query(pattern="^(dump|spike)$", description="Filter by event type"),
    ] = None,
    severity: Annotated[
        str | None,
        Query(pattern="^(ok|good|great)$", description="Filter by minimum severity"),
    ] = None,
    item_id: Annotated[int | None, Query(description="Filter by item ID")] = None,
    hours_ago: Annotated[
        int | None, Query(ge=1, description="Only show events from last N hours")
    ] = None,
    # Sorting
    sort_by: Annotated[
        str,
        Query(
            pattern="^(detected_at|price_change_percent|volume_change_percent)$",
            description="Field to sort by",
        ),
    ] = "detected_at",
    sort_order: Annotated[
        str, Query(pattern="^(asc|desc)$", description="Sort order")
    ] = "desc",
):
    """
    Get dump/spike events with pagination and filtering.

    Example requests:
    - /api/dumps                         # Latest 25 events
    - /api/dumps?event_type=dump         # Only dumps
    - /api/dumps?event_type=spike        # Only spikes
    - /api/dumps?item_id=2&hours_ago=24  # Events for item 2 in last 24 hours
    """
    query = select(DumpEvent)

    # Apply filters
    if event_type:
        query = query.where(DumpEvent.event_type == event_type)

    if severity:
        # Filter by minimum severity (great > good > ok)
        if severity == "great":
            query = query.where(DumpEvent.severity == "great")
        elif severity == "good":
            query = query.where(DumpEvent.severity.in_(["good", "great"]))
        # "ok" shows all, no filter needed

    if item_id:
        query = query.where(DumpEvent.item_id == item_id)

    if hours_ago:
        cutoff = datetime.utcnow() - timedelta(hours=hours_ago)
        query = query.where(DumpEvent.detected_at >= cutoff)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Apply sorting
    sort_column = getattr(DumpEvent, sort_by, DumpEvent.detected_at)
    # For price_change_percent, sort by absolute value (biggest swings first)
    if sort_by == "price_change_percent":
        if sort_order == "desc":
            query = query.order_by(func.abs(col(sort_column)).desc())
        else:
            query = query.order_by(func.abs(col(sort_column)).asc())
    else:
        if sort_order == "desc":
            query = query.order_by(col(sort_column).desc())
        else:
            query = query.order_by(col(sort_column).asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    events = session.exec(query).all()

    return {
        "events": events,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


@router.get("/{event_id}")
def get_dump_event(
    event_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Get a single dump/spike event by ID."""
    query = select(DumpEvent).where(DumpEvent.id == event_id)
    event = session.exec(query).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event
