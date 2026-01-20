from fastapi import APIRouter

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


# TODO: Implement item endpoints


# GET 	/api/items 	List items with pagination & filtering
# Connect to DB and fetch items
@router.get("/items")
def list_items():
    pass


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
