from sqlmodel import SQLModel, Field
from datetime import datetime
from aggregator.util.margin import ge_margin

# --- Helper functions ---
def safe_int(val):
    """Return val if it's a valid int, else 0."""
    return val if isinstance(val, int) and val is not None else 0

def safe_nullable_int(val):
    """Return val if it's a valid int, else None."""
    return val if isinstance(val, int) else None

class Item(SQLModel, table=True):
    # Identification
    id: int | None = Field(default=None, primary_key=True)
    item_name: str = Field(default="Unknown")

    # Price data
    high: int = Field(default=0)           # Latest high price
    high_time: int = Field(default=0)      # Timestamp for high price
    low: int = Field(default=0)            # Latest low price
    low_time: int = Field(default=0)       # Timestamp for low price
    margin: int = Field(default=0)         # Calculated margin (high - low - tax)

    # Volume data
    volume: int = Field(default=0)         # Latest total volume
    avg_high_price: int | None = Field(default=None)   # Average high price (5m series)
    high_price_volume: int = Field(default=0)          # Volume at high price (5m series)
    avg_low_price: int | None = Field(default=None)    # Average low price (5m series)
    low_price_volume: int = Field(default=0)           # Volume at low price (5m series)

    @classmethod
    def from_raw(cls, item_id, name_mapping, prices, volume_data, volume_5m_data=None):

        def safe_int(val):
            """Return val if it's a valid int, else 0."""
            return val if isinstance(val, int) and val is not None else 0

        def safe_nullable_int(val):
            """Return val if it's a valid int, else None."""
            return val if isinstance(val, int) else None

        high = safe_int(prices.get("high"))
        low = safe_int(prices.get("low"))
        high_time = safe_int(prices.get("highTime"))
        low_time = safe_int(prices.get("lowTime"))
        # Default volume from main volume API
        volume = safe_int(volume_data.get("data", {}).get(item_id))
    @classmethod
    def from_raw(cls, item_id, name_mapping, prices, volume_data, volume_5m_data=None):
        """
        Create an Item instance from raw API data.
        Prioritizes 5m volume/price data if available.
        """
        # --- Extract basic price and time data ---
        high = safe_int(prices.get("high"))
        low = safe_int(prices.get("low"))
        high_time = safe_int(prices.get("highTime"))
        low_time = safe_int(prices.get("lowTime"))

        # --- Extract volume from main API by default ---
        volume = safe_int(volume_data.get("data", {}).get(item_id))

        # --- Extract 5m series data if available ---
        avg_high_price = None
        high_price_volume = 0
        avg_low_price = None
        low_price_volume = 0
        if volume_5m_data:
            item_5m = volume_5m_data.get("data", {}).get(item_id, {})
            # Prefer 5m totalVolume for volume if present
            if "totalVolume" in item_5m:
                volume = safe_int(item_5m.get("totalVolume"))
            avg_high_price = safe_nullable_int(item_5m.get("avgHighPrice"))
            high_price_volume = safe_int(item_5m.get("highPriceVolume"))
            avg_low_price = safe_nullable_int(item_5m.get("avgLowPrice"))
            low_price_volume = safe_int(item_5m.get("lowPriceVolume"))

        # --- Calculate margin ---
        margin = ge_margin(high, low)

        # --- Construct and return Item instance ---
        return cls(
            id=int(item_id),
            item_name=name_mapping.get(item_id, "Unknown"),
            high=high,
            high_time=high_time,
            low=low,
            low_time=low_time,
            margin=margin,
            volume=volume,
            avg_high_price=avg_high_price,
            high_price_volume=high_price_volume,
            avg_low_price=avg_low_price,
            low_price_volume=low_price_volume
        )
