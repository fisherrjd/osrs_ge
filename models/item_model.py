from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_name: str = Field(default="Unknown")
    high: int = Field(default=0)
    high_time: int = Field(default=0)
    low: int = Field(default=0)
    low_time: int = Field(default=0)
    margin: int = Field(default=0)
    volume: int = Field(default=0)