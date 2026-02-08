import os

import requests
from sqlmodel import Session, SQLModel, create_engine

from api.schemas.data_models import (
    LatestData,
    MappingData,
    MappingList,
    Volume24h,
)
from api.schemas.item_model import Item
from api.util.margin import ge_margin

LATEST_API_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
MAPPING_API_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
VOLUME_API_URL = "https://prices.runescape.wiki/api/v1/osrs/volumes"

HEADERS = {
    "User-Agent": "@PapaBear#2007",
    "From": "dev@jade.rip",
}
DB_FILE = os.getenv("DB_FILE", "sqlite:///item_data.db")

engine = create_engine(DB_FILE)

SQLModel.metadata.create_all(engine)


def fetch_data(api_url) -> dict:
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def mapping_wrapper() -> MappingList:
    data = fetch_data(MAPPING_API_URL)
    return MappingList(items=[MappingData(**item) for item in data])


def latest_wrapper() -> LatestData:
    data = fetch_data(LATEST_API_URL)
    return LatestData(**data)


def volume_wrapper() -> Volume24h:
    data = fetch_data(VOLUME_API_URL)
    return Volume24h(**data)


def update_database(
    latest_data: LatestData, mapping_data: MappingList, volume_data: Volume24h
):
    """Update the database with the latest item data."""
    # Build mapping from item id to MappingData
    mapping_dict = {item.id: item for item in mapping_data.items}
    # Volume data is Dict[str, int], keys are string ids
    volume_dict = volume_data.data

    with Session(engine) as session:
        for item_id, prices in latest_data.data.items():
            mapping_info = mapping_dict.get(item_id)
            if not mapping_info:
                continue  # skip items not in mapping
            volume_info = volume_dict.get(str(item_id), 0)

            # Calculate margin
            high_price = prices.high or 0
            low_price = prices.low or 0
            margin = ge_margin(high_price, low_price)

            # Create Item object (adjust fields as needed)
            item = Item(
                id=item_id,
                name=mapping_info.name,
                examine=mapping_info.examine,
                members=mapping_info.members,
                lowalch=mapping_info.lowalch,
                limit=mapping_info.limit,
                value=mapping_info.value,
                highalch=mapping_info.highalch,
                icon=mapping_info.icon,
                high=prices.high,
                highTime=prices.highTime,
                low=prices.low,
                lowTime=prices.lowTime,
                volume_24h=volume_info,
                margin=margin,
            )
            session.merge(item)
        session.commit()


if __name__ == "__main__":
    print("Fetching latest prices, mapping, and 24h volume data...")
    mapping_data = mapping_wrapper()
    latest_data = latest_wrapper()
    volume_data = volume_wrapper()

    update_database(latest_data, mapping_data, volume_data)
    print("Item table updated successfully!")
