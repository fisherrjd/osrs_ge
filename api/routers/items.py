import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select

from api.db.item_data import engine
from api.schemas.item_model import Item
from api.schemas.item_volume_5m import ItemSnapshot

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session


# GET 	/api/items 	List items with pagination & filtering
@router.get("")
def get_items(
    # Database session
    session: Annotated[Session, Depends(get_session)],
    # Pagination parameters
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return")] = 25,
    # Filter parameters
    members: Annotated[
        bool | None, Query(description="Filter by members status")
    ] = None,
    min_volume: Annotated[
        int | None, Query(ge=0, description="Minimum 24h volume")
    ] = None,
    max_volume: Annotated[
        int | None, Query(ge=0, description="Maximum 24h volume")
    ] = None,
    min_price: Annotated[
        int | None, Query(ge=0, description="Minimum high price")
    ] = None,
    max_price: Annotated[int | None, Query(description="Maximum high price")] = None,
    min_margin: Annotated[
        int | None, Query(description="Minimum margin (profit after GE tax)")
    ] = None,
    max_margin: Annotated[
        int | None, Query(description="Maximum margin (profit after GE tax)")
    ] = None,
    name: Annotated[
        str | None, Query(description="Search by name (case-insensitive)")
    ] = None,
    max_time_ago: Annotated[
        int | None, Query(ge=0, description="Maximum minutes ago for price data")
    ] = None,
    # Sorting
    sort_by: Annotated[str, Query(description="Field to sort by")] = "volume_24h",
    sort_order: Annotated[
        str, Query(pattern="^(asc|desc)$", description="Sort order")
    ] = "desc",
):
    """
    Get items with pagination and filtering.

    Example requests:
    - /api/items?limit=20                          # First 20 items
    - /api/items?skip=20&limit=20                  # Next 20 items
    - /api/items?members=true&min_volume=10000     # Members items with volume > 10k
    - /api/items?name=dragon&sort_by=high          # Dragon items sorted by price
    """
    # Start building the query
    query = select(Item)

    # Apply filters
    if members is not None:
        query = query.where(Item.members == members)

    if min_volume is not None:
        query = query.where(Item.volume_24h >= min_volume)

    if max_volume is not None:
        query = query.where(Item.volume_24h <= max_volume)

    if min_price is not None:
        query = query.where(col(Item.high) >= min_price)

    if max_price is not None:
        query = query.where(col(Item.high) <= max_price)

    if min_margin is not None:
        query = query.where(Item.margin >= min_margin)

    if max_margin is not None:
        query = query.where(Item.margin <= max_margin)

    if name is not None:
        # Case-insensitive search using LIKE
        query = query.where(col(Item.name).ilike(f"%{name}%"))

    if max_time_ago is not None:
        # Filter by timestamp - only show items updated within the last N minutes
        # Convert minutes to seconds and calculate cutoff timestamp
        cutoff_timestamp = int(time.time()) - (max_time_ago * 60)
        # Item must have either highTime or lowTime within the time window
        # Also check that the timestamp is not NULL
        query = query.where(
            (
                (col(Item.highTime).is_not(None))
                & (col(Item.highTime) >= cutoff_timestamp)
            )
            | (
                (col(Item.lowTime).is_not(None))
                & (col(Item.lowTime) >= cutoff_timestamp)
            )
        )

    # Get total count (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Apply sorting
    sort_column = getattr(Item, sort_by, Item.volume_24h)
    if sort_order == "desc":
        query = query.order_by(col(sort_column).desc())
    else:
        query = query.order_by(col(sort_column).asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    items = session.exec(query).all()

    # Return with metadata
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


# GET 	/api/items/{id} 	Get single item with current prices
@router.get("/{item_id}")
def read_item(
    item_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Get a single item by ID."""
    query = select(Item).where(Item.id == item_id)
    item = session.exec(query).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


# GET 	/api/items/search?q={query} 	Fuzzy search by name
#
# GET 	/api/items/top-margins 	Top margin opportunities
#
# GET 	/api/items/top-volume 	Highest volume items


# Time period configurations for chart views
# Maps period name to (hours_of_data, bucket_size_in_hours)
CHART_PERIODS = {
    "1d": (24, None),  # 1 day: raw 5-min data (no aggregation)
    "1w": (168, 1),  # 1 week: hourly averages
    "1m": (720, 6),  # 1 month (30 days): 6-hour averages
    "6m": (4320, 24),  # 6 months (180 days): daily averages
}


@router.get("/{item_id}/history")
def get_item_history(
    item_id: int,
    session: Annotated[Session, Depends(get_session)],
    period: Annotated[
        str,
        Query(
            pattern="^(1d|1w|1m|6m)$",
            description="Time period: 1d (5min), 1w (hourly), 1m (6hr), 6m (daily)",
        ),
    ] = "1d",
):
    """
    Get time series data for an item with appropriate aggregation per period.

    Periods and their resolutions:
    - 1d: Raw 5-minute snapshots (288 data points)
    - 1w: Hourly averages (168 data points)
    - 1m: 6-hour averages (~120 data points)
    - 6m: Daily averages (~180 data points)

    Example requests:
    - /api/items/2/history              # Last 24 hours, 5-min resolution
    - /api/items/2/history?period=1w    # Last week, hourly resolution
    - /api/items/2/history?period=1m    # Last month, 6-hour resolution
    - /api/items/2/history?period=6m    # Last 6 months, daily resolution
    """
    from datetime import datetime, timedelta

    # Verify item exists
    item_query = select(Item).where(Item.id == item_id)
    item = session.exec(item_query).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    hours_back, bucket_hours = CHART_PERIODS[period]
    cutoff = datetime.utcnow() - timedelta(hours=hours_back)

    if bucket_hours is None:
        # Raw 5-minute data for 1d view
        query = (
            select(ItemSnapshot)
            .where(ItemSnapshot.item_id == item_id)
            .where(ItemSnapshot.timestamp >= cutoff)
            .order_by(col(ItemSnapshot.timestamp).asc())
        )
        snapshots = session.exec(query).all()

        return {
            "item_id": item_id,
            "item_name": item.name,
            "period": period,
            "resolution": "5m",
            "count": len(snapshots),
            "data": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "avg_high_price": s.avg_high_price,
                    "avg_low_price": s.avg_low_price,
                    "high_price_volume": s.high_price_volume,
                    "low_price_volume": s.low_price_volume,
                    "total_volume": s.total_volume,
                }
                for s in snapshots
            ],
        }

    # Aggregated data for longer periods
    # Fetch raw data and aggregate in Python (SQLite strftime aggregation is limited)
    query = (
        select(ItemSnapshot)
        .where(ItemSnapshot.item_id == item_id)
        .where(ItemSnapshot.timestamp >= cutoff)
        .order_by(col(ItemSnapshot.timestamp).asc())
    )
    snapshots = session.exec(query).all()

    # Group snapshots into time buckets
    buckets: dict[str, list[ItemSnapshot]] = {}
    for s in snapshots:
        # Calculate bucket key based on bucket_hours
        bucket_time = s.timestamp.replace(
            hour=(s.timestamp.hour // bucket_hours) * bucket_hours,
            minute=0,
            second=0,
            microsecond=0,
        )
        bucket_key = bucket_time.isoformat()
        if bucket_key not in buckets:
            buckets[bucket_key] = []
        buckets[bucket_key].append(s)

    # Aggregate each bucket
    aggregated = []
    for timestamp, bucket_snapshots in sorted(buckets.items()):
        high_prices = [s.avg_high_price for s in bucket_snapshots if s.avg_high_price]
        low_prices = [s.avg_low_price for s in bucket_snapshots if s.avg_low_price]
        high_volumes = [
            s.high_price_volume for s in bucket_snapshots if s.high_price_volume
        ]
        low_volumes = [
            s.low_price_volume for s in bucket_snapshots if s.low_price_volume
        ]
        total_volumes = [s.total_volume for s in bucket_snapshots if s.total_volume]

        aggregated.append(
            {
                "timestamp": timestamp,
                "avg_high_price": sum(high_prices) / len(high_prices)
                if high_prices
                else None,
                "avg_low_price": sum(low_prices) / len(low_prices)
                if low_prices
                else None,
                "high_price_volume": sum(high_volumes) if high_volumes else None,
                "low_price_volume": sum(low_volumes) if low_volumes else None,
                "total_volume": sum(total_volumes) if total_volumes else None,
            }
        )

    resolution_labels = {"1w": "1h", "1m": "6h", "6m": "1d"}

    return {
        "item_id": item_id,
        "item_name": item.name,
        "period": period,
        "resolution": resolution_labels.get(period, "5m"),
        "count": len(aggregated),
        "data": aggregated,
    }
