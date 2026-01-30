from datetime import datetime

from sqlmodel import Field, SQLModel


class DumpEvent(SQLModel, table=True):
    """Represents a detected price dump or spike event."""

    __tablename__ = "dump_events"

    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(index=True)
    item_name: str
    event_type: str = Field(index=True)  # "dump" or "spike"
    detected_at: datetime = Field(index=True)

    # Price data
    trigger_price: float  # Price that triggered the event
    baseline_price: float  # Rolling average price before event
    price_change_percent: float  # Percentage change from baseline

    # Volume data
    trigger_volume: int  # Volume in the triggering snapshot
    baseline_volume: float  # Rolling average volume
    volume_change_percent: float  # Percentage change from baseline
