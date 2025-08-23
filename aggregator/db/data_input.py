from sqlmodel import SQLModel, create_engine, Session
from aggregator.models.item_model import Item
from aggregator.models.item_volume_5m import ItemSnapshot
import requests
import time
from datetime import datetime, timezone

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


def fetch_data(api_url):
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def fetch_all_data():
    """Fetch mapping, latest prices, and volume data from APIs."""
    mapping_data = fetch_data(MAPPING_API_URL)
    latest_data = fetch_data(LATEST_API_URL)
    volume_data = fetch_data(VOLUME_API_URL)
    volume_5m_data = fetch_data(VOLUME_5M_API_URL)
    return mapping_data, latest_data, volume_data, volume_5m_data


def update_database(latest_data, mapping_data, volume_data):
    """Update the database with the latest item data."""

    def update_database_inner(latest_data, mapping_data, volume_data):
        name_mapping = {
            str(item["id"]): item.get("name", "Unknown") for item in mapping_data
        }
        for item_id, prices in latest_data["data"].items():
            item = Item.from_raw(item_id, name_mapping, prices, volume_data)
            session.merge(item)
        session.commit()

    return update_database_inner


def ingest_api_data(api_json: dict):
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        for item_id, item_data in api_json["data"].items():
            high_vol = item_data.get("highPriceVolume", 0) or 0
            low_vol = item_data.get("lowPriceVolume", 0) or 0
            total_vol = high_vol + low_vol

            record = ItemSnapshot(
                item_id=int(item_id),
                timestamp=now,
                avg_high_price=item_data.get("avgHighPrice"),
                high_price_volume=high_vol,
                avg_low_price=item_data.get("avgLowPrice"),
                low_price_volume=low_vol,
                total_volume=total_vol,
            )
            session.add(record)
        session.commit()


# Run main every minute if this script is executed directly
if __name__ == "__main__":
    run_count = 0
    while True:
        mapping_data, latest_data, volume_data, volume_5m_data = fetch_all_data()
        update_database_inner = update_database(latest_data, mapping_data, volume_data)
        update_database_inner(latest_data, mapping_data, volume_data)
        if run_count % 5 == 0:
            ingest_api_data(volume_5m_data)
            print("ItemVolume5m table updated!")
        print("Data saved successfully!")
        print("Waiting 60 seconds for next run...")
        run_count += 1
        time.sleep(60)
