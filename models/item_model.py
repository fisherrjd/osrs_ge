
from sqlmodel import SQLModel, Field
from datetime import datetime
from util.margin import ge_margin

class Item(SQLModel, table=True):
    avg_high_price: int | None = Field(default=None)
    high_price_volume: int = Field(default=0)
    avg_low_price: int | None = Field(default=None)
    low_price_volume: int = Field(default=0)
    id: int | None = Field(default=None, primary_key=True)
    item_name: str = Field(default="Unknown")
    high: int = Field(default=0)
    high_time: int = Field(default=0)
    low: int = Field(default=0)
    low_time: int = Field(default=0)
    margin: int = Field(default=0)
    volume: int = Field(default=0)

    @classmethod
    def from_raw(cls, item_id, name_mapping, prices, volume_data, volume_5m_data=None):
        def safe_int(val):
            return val if isinstance(val, int) and val is not None else 0

        def safe_nullable_int(val):
            return val if isinstance(val, int) else None

        high = safe_int(prices.get("high"))
        low = safe_int(prices.get("low"))
        high_time = safe_int(prices.get("highTime"))
        low_time = safe_int(prices.get("lowTime"))
        # Default volume from main volume API
        volume = safe_int(volume_data.get("data", {}).get(item_id))
    # volume_5m removed
        avg_high_price = None
        high_price_volume = 0
        avg_low_price = None
        low_price_volume = 0
        # If 5m API is available, prefer its volume and stats
        if volume_5m_data:
            item_5m = volume_5m_data.get("data", {}).get(item_id, {})
            # Use totalVolume from 5m API for volume if present
            if "totalVolume" in item_5m:
                volume = safe_int(item_5m.get("totalVolume"))
            # volume_5m removed
            avg_high_price = safe_nullable_int(item_5m.get("avgHighPrice"))
            high_price_volume = safe_int(item_5m.get("highPriceVolume"))
            avg_low_price = safe_nullable_int(item_5m.get("avgLowPrice"))
            low_price_volume = safe_int(item_5m.get("lowPriceVolume"))
        margin = ge_margin(high, low)
        return cls(
            id=int(item_id),
            item_name=name_mapping.get(item_id, "Unknown"),
            high=high,
            high_time=high_time,
            low=low,
            low_time=low_time,
            margin=margin,
            volume=volume,
            # volume_5m removed
            avg_high_price=avg_high_price,
            high_price_volume=high_price_volume,
            avg_low_price=avg_low_price,
            low_price_volume=low_price_volume
        )

    item_name: str = Field(default="Unknown")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_int_fields

    @classmethod
    def validate_int_fields(cls, values):
        int_fields = ["high", "high_time", "low", "low_time", "margin", "volume"]
        for field in int_fields:
            value = values.get(field)
            if value is None or not isinstance(value, int):
                values[field] = 0
        return values
