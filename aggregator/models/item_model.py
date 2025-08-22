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
    high: int = Field(default=0)  # Latest high price
    high_time: int = Field(default=0)  # Timestamp for high price
    low: int = Field(default=0)  # Latest low price
    low_time: int = Field(default=0)  # Timestamp for low price
    margin: int = Field(default=0)  # Calculated margin (high - low - tax)

    # Volume data
    volume: int = Field(default=0)  # Latest total volume
    # ...existing code...

    @classmethod
    def from_raw(cls, item_id, name_mapping, prices, volume_data, volume_5m_data=None):
        """
        Create an Item instance from raw API data.
        """
        # --- Extract basic price and time data ---
        high = safe_int(prices.get("high"))
        low = safe_int(prices.get("low"))
        high_time = safe_int(prices.get("highTime"))
        low_time = safe_int(prices.get("lowTime"))

        # --- Extract volume from main API by default ---
        volume = safe_int(volume_data.get("data", {}).get(item_id))

        # ...existing code...

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
        )
