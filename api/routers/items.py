import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select

from api.db.item_data import engine
from api.schemas.item_model import Item

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
# GET 	/api/items/{id}/history 	Historical OHLCV data for charts
#
# GET 	/api/items/top-margins 	Top margin opportunities
#
# GET 	/api/items/top-volume 	Highest volume items
