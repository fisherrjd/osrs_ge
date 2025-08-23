from sqlmodel import SQLModel, Field
from datetime import datetime
from aggregator.util.margin import ge_margin


# --- Helper functions ---
def safe_int(val):
    """Return val if it's a valid int, else 0."""
    return val if isinstance(val, int) and val is not None else 0


class Item(SQLModel, table=True):
    # Identification
    id: int | None = Field(default=None, primary_key=True)
    item_name: str = Field(default="Unknown")

    # Price data
    high: int = Field(default=0)  # Latest Insta Buy Price
    high_time: int = Field(default=0)  # Timestamp for Insta Buy Price
    low: int = Field(default=0)  # Latest Insta Sell Price
    low_time: int = Field(default=0)  # Timestamp for Insta Sell Price
    margin: int = Field(default=0)  # Calculated margin (high - low - tax)
    # Volume data
    volume: int = Field(default=0)  # 24h Time series volume data
