import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, func, select

from api.db.news_data import engine
from api.schemas.news_models import NewsItem

router = APIRouter(
    prefix="/news",
    tags=["news"],
)


def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session


# GET 	/api/items 	List items with pagination & filtering
@router.get("")
def get_news(
    session: Annotated[Session, Depends(get_session)],
):
    """Get a list of news items."""
    query = select(NewsItem).order_by(col(NewsItem.score).desc())
    items = session.exec(query).all()

    return items
