from sqlmodel import SQLModel, create_engine, Session
from models.item_model import Item
import requests

LATEST_API_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
MAPPING_API_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
VOLUME_API_URL = "https://prices.runescape.wiki/api/v1/osrs/volumes"
VOLUME_5M_API_URL = "https://prices.runescape.wiki/api/v1/osrs/5m"

HEADERS = {
    "User-Agent": "@PapaBear#2007",
    "From": "dev@jade.rip",
}
DB_FILE = "sqlite:///mydb.sqlite3"

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
    def update_database_inner(latest_data, mapping_data, volume_data, volume_5m_data):
        name_mapping = {str(item["id"]): item.get("name", "Unknown") for item in mapping_data}
        for item_id, prices in latest_data["data"].items():
            item = Item.from_raw(item_id, name_mapping, prices, volume_data, volume_5m_data)
            session.merge(item)
        session.commit()
    return update_database_inner

def main():
    """Main function to fetch data and save to the database every minute."""
    try:
        mapping_data, latest_data, volume_data, volume_5m_data = fetch_all_data()
        update_database_inner = update_database(latest_data, mapping_data, volume_data)
        update_database_inner(latest_data, mapping_data, volume_data, volume_5m_data)
        print("Data saved successfully!")
    except Exception as e:
        print(f"Error: {e}")
    


# Run main every minute if this script is executed directly
import time
if __name__ == "__main__":
    while True:
        main()
        print("Waiting 60 seconds for next run...")
        time.sleep(60)
