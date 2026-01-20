from sqlmodel import SQLModel, Field
from datetime import datetime


class ItemSnapshot(SQLModel, table=True):
    __tablename__ = "itemsnapshot"
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(index=True)
    timestamp: datetime = Field(index=True)
    avg_high_price: float | None = None
    high_price_volume: int | None = None
    avg_low_price: float | None = None
    low_price_volume: int | None = None
    total_volume: int | None = None  # 1<-- sum of both volumes
