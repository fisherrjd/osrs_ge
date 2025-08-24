from typing import Dict, Optional, List
from pydantic import BaseModel
from aggregator.util.averages import get_average_field


class MappingData(BaseModel):
    examine: str
    id: int
    members: bool
    lowalch: Optional[int] = 0
    highalch: Optional[int] = 0
    limit: Optional[int] = 0
    value: Optional[int] = 0
    icon: Optional[str] = ""
    name: str


class MappingList(BaseModel):
    items: List[MappingData]


class ItemData(BaseModel):
    high: Optional[int] = None
    highTime: Optional[int] = None
    low: Optional[int] = None
    lowTime: Optional[int] = None


class LatestData(BaseModel):

    data: Dict[int, ItemData]


class Volume24h(BaseModel):
    timestamp: Optional[int] = 0
    data: Dict[str, Optional[int]]


class Volume5mItem(BaseModel):
    avgHighPrice: Optional[int] = None
    highPriceVolume: Optional[int] = 0
    avgLowPrice: Optional[int] = None
    lowPriceVolume: Optional[int] = 0


class Volume5m(BaseModel):
    data: Dict[str, Volume5mItem]

    @property
    def avg_high_price(self) -> Optional[float]:
        return get_average_field(self, "avgHighPrice")

    @property
    def avg_high_volume(self) -> Optional[float]:
        return get_average_field(self, "highPriceVolume")

    @property
    def avg_low_price(self) -> Optional[float]:
        return get_average_field(self, "avgLowPrice")

    @property
    def avg_low_volume(self) -> Optional[float]:
        return get_average_field(self, "lowPriceVolume")
