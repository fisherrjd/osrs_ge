from sqlmodel import SQLModel, Field
from datetime import datetime

class ItemVolume5m(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(index=True)
    timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    volume_5m: int = Field(default=0)
    avg_high_price: int | None = Field(default=None)
    high_price_volume: int = Field(default=0)
    avg_low_price: int | None = Field(default=None)
    low_price_volume: int = Field(default=0)

    # Optionally, you can add a __repr__ for easier debugging
    def __repr__(self):
        return (f"<ItemVolume5m item_id={self.item_id} timestamp={self.timestamp} "
                f"volume_5m={self.volume_5m}>")
