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
    name: str = Field(default="Unknown")
    examine: str = Field(default="")
    members: bool = Field(default=False)
    lowalch: int = Field(default=0)
    limit: int = Field(default=0)
    value: int = Field(default=0)
    highalch: int = Field(default=0)
    icon: str = Field(default="")
    high: int = Field(default=0)
    highTime: int = Field(default=0)
    low: int = Field(default=0)
    lowTime: int = Field(default=0)
    volume_24h: int = Field(default=0)
