from aggregator.models.item_model import Item
from aggregator.models.item_volume_5m import ItemSnapshot
from aggregator.models.data_models import (
    MappingData,
    MappingList,
    LatestData,
    Volume24h,
    Volume5m,
)
from datetime import datetime, timezone
from sqlmodel import SQLModel, create_engine, Session
import requests
import time


LATEST_API_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
MAPPING_API_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
VOLUME_API_URL = "https://prices.runescape.wiki/api/v1/osrs/volumes"
VOLUME_5M_API_URL = "https://prices.runescape.wiki/api/v1/osrs/5m"

HEADERS = {
    "User-Agent": "@PapaBear#2007",
    "From": "dev@jade.rip",
}
DB_FILE = "sqlite:///item_data.db"

engine = create_engine(DB_FILE)
session = Session(engine)
SQLModel.metadata.create_all(engine)


def fetch_data(api_url) -> dict:
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


# TODO make nice


def mapping_wrapper() -> MappingList:
    data = fetch_data(MAPPING_API_URL)
    return MappingList(items=[MappingData(**item) for item in data])


def latest_wrapper() -> LatestData:
    data = fetch_data(LATEST_API_URL)
    return LatestData(**data)


def volume_wrapper() -> Volume24h:
    data = fetch_data(VOLUME_API_URL)
    return Volume24h(**data)


def volume5m_wrapper() -> Volume5m:
    data = fetch_data(VOLUME_5M_API_URL)
    return Volume5m.model_validate(data)


def fetch_all_data() -> tuple[MappingList, LatestData, Volume24h, Volume5m]:
    """Fetch mapping, latest prices, and volume data from APIs."""
    # TODO: Create data models and handle this nicely with their own methods
    mapping_data = mapping_wrapper()
    latest_data = latest_wrapper()
    volume_data = volume_wrapper()
    volume_5m_data = volume5m_wrapper()
    return mapping_data, latest_data, volume_data, volume_5m_data


def update_database(latest_data, mapping_data, volume_data):
    """Update the database with the latest item data."""

    def update_database_inner(latest_data, mapping_data, volume_data):
        # Build mapping from item id to MappingData
        mapping_dict = {item.id: item for item in mapping_data.items}
        # Volume data is Dict[str, int], keys are string ids
        volume_dict = volume_data.data

        for item_id, prices in latest_data.data.items():
            mapping_info = mapping_dict.get(item_id)
            if not mapping_info:
                continue  # skip items not in mapping
            volume_info = volume_dict.get(str(item_id), 0)
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
            )
            session.merge(item)
        session.commit()

    return update_database_inner


def save_volume5m_to_db(volume_5m_data: Volume5m, engine):
    """Save Volume5m pydantic model data to ItemSnapshot SQLModel table."""
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        for item_id, item_data in volume_5m_data.data.items():
            high_vol = item_data.highPriceVolume or 0
            low_vol = item_data.lowPriceVolume or 0
            total_vol = high_vol + low_vol
            record = ItemSnapshot(
                item_id=int(item_id),
                timestamp=now,
                avg_high_price=item_data.avgHighPrice,
                high_price_volume=high_vol,
                avg_low_price=item_data.avgLowPrice,
                low_price_volume=low_vol,
                total_volume=total_vol,
            )
            session.add(record)
        session.commit()


# Remove ingest_api_data function

# Run main every minute if this script is executed directly
if __name__ == "__main__":
    run_count = 0
    while True:
        mapping_data, latest_data, volume_data, volume_5m_data = fetch_all_data()
        update_database_inner = update_database(latest_data, mapping_data, volume_data)
        update_database_inner(latest_data, mapping_data, volume_data)
        if run_count % 5 == 0:
            save_volume5m_to_db(volume_5m_data, engine)
            print("ItemVolume5m table updated!")
        print("Data saved successfully!")
        print("Waiting 60 seconds for next run...")
        run_count += 1
        time.sleep(60)
