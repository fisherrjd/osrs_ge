from typing import Dict, Optional, List
from pydantic import BaseModel


class MappingData(BaseModel):
    examine: str
    id: int
    members: bool
    lowalch: int
    limit: int
    value: int
    highalch: int
    icon: str
    name: str


class MappingList(BaseModel):
    items: List[MappingData]


class ItemData(BaseModel):
    high: int
    highTime: int
    low: int
    lowTime: int


class LatestData(BaseModel):
    data: Dict[int, ItemData]


class Volume24h(BaseModel):
    timestamp: int
    data: Dict[str, int]


class Volume5mItem(BaseModel):
    avgHighPrice: Optional[int]
    highPriceVolume: int
    avgLowPrice: Optional[int]
    lowPriceVolume: int


class Volume5m(BaseModel):

    data: Dict[str, Volume5mItem]
