from typing import Dict, Optional, List
from pydantic import BaseModel


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
    high: Optional[int] = 0
    highTime: Optional[int] = 0
    low: Optional[int] = 0
    lowTime: Optional[int] = 0


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
