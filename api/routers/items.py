from typing import Annotated

from fastapi import APIRouter, Depends, Query
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
    # Pagination parameters
    skip: Annotated[int, Query(default=0, ge=0, description="Number of items to skip")],
    limit: Annotated[
        int, Query(default=50, ge=1, le=100, description="Max items to return")
    ],
    # Filter parameters
    members: Annotated[
        bool | None, Query(default=None, description="Filter by members status")
    ],
    min_volume: Annotated[
        int | None, Query(default=None, ge=0, description="Minimum 24h volume")
    ],
    max_volume: Annotated[
        int | None, Query(default=None, ge=0, description="Maximum 24h volume")
    ],
    min_price: Annotated[
        int | None, Query(default=None, ge=0, description="Minimum high price")
    ],
    max_price: Annotated[
        int | None, Query(default=None, description="Maximum high price")
    ],
    min_margin: Annotated[
        int | None,
        Query(default=None, description="Minimum margin (profit after GE tax)"),
    ],
    max_margin: Annotated[
        int | None,
        Query(default=None, description="Maximum margin (profit after GE tax)"),
    ],
    name: Annotated[
        str | None,
        Query(default=None, description="Search by name (case-insensitive)"),
    ],
    # Sorting
    sort_by: Annotated[
        str, Query(default="volume_24h", description="Field to sort by")
    ],
    sort_order: Annotated[
        str, Query(default="desc", pattern="^(asc|desc)$", description="Sort order")
    ],
    # Database session
    session: Annotated[Session, Depends(get_session)],
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
# @router.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# GET 	/api/items/search?q={query} 	Fuzzy search by name
#
# GET 	/api/items/{id}/history 	Historical OHLCV data for charts
#
# GET 	/api/items/top-margins 	Top margin opportunities
#
# GET 	/api/items/top-volume 	Highest volume items
