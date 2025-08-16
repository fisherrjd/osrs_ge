from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from models.item_model import Item
import requests
import json

# Define the API URLs
LATEST_API_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
MAPPING_API_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
VOLUME_API_URL = "https://prices.runescape.wiki/api/v1/osrs/volumes"

HEADERS = {
    "User-Agent": "@PapaBear#2007",
    "From": "dev@jade.rip",
}
DB_FILE = "sqlite:///mydb.sqlite3"

engine = create_engine(DB_FILE)
Session = sessionmaker(bind=engine)
session = Session()

SQLModel.metadata.create_all(engine)



def fetch_data(api_url):
    """Fetch data from the given API.

    Raises:
        Exception: Response for a failed api request

    Returns:
        returns json of item data
    """
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def process_mapping_data(mapping_data) -> dict:
    """Process mapping data to create a dictionary of item_id -> name.

    Args:
        mapping_data: data to be processed

    Returns:
        returns mapped dictionary of item ID and item name
    """
    name_mapping = [Item]
    for item in mapping_data:
        item_id = str(item.get("id", ""))
        name = item.get("name", "Unknown")
        if item_id:
            name_mapping[item_id] = name
    return name_mapping

def aggregate_items(latest_data, mapping_data, volume_data):
    """Aggregate the latest data, mapping data, and volume data into Item objects.

    Args:
        latest_data: The latest price data for items.
        mapping_data: The mapping data to get item names.
        volume_data: The volume data for items.

    Returns:
        A list of Item objects with aggregated data.
    """
    name_mapping = {str(item["id"]): item.get("name", "Unknown") for item in mapping_data}
    items = []
    for item_id, prices in latest_data["data"].items():
        item = Item(
            id=int(item_id),
            item_name=name_mapping.get(item_id, "Unknown"),
            high=prices.get("high", 0),
            high_time=prices.get("highTime", 0),
            low=prices.get("low", 0),
            low_time=prices.get("lowTime", 0),
            margin=prices.get("high", 0) - prices.get("low", 0),
            volume=volume_data.get("data", {}).get(item_id, 0)
        )
        items.append(item)
    return items

def main():
    """Main function to fetch data and save to the database every minute."""
    try:
        # Fetch item mapping data (item_id to name)
        mapping_data = fetch_data(MAPPING_API_URL)

        # Fetch the latest item prices
        latest_data = fetch_data(LATEST_API_URL)

        # Fetch volume data
        volume_data = fetch_data(VOLUME_API_URL)
        
        # Aggregate all data into Item objects
        items = aggregate_items(latest_data, mapping_data, volume_data)

        # Pretty print the items as JSON
        print(json.dumps([item.dict() for item in items], indent=2))
        # Save the data to the database
        # save_to_db(latest_data, volume_data, name_mapping, DB_FILE)
        print("Data saved successfully!")

    except Exception as e:
        print(f"Error: {e}")
    
    # Example: items_data = [{'name': 'item1', 'price': 100}, ...]
    # items = [Item(**data) for data in items_data]
    # session.add_all(items)
    # session.commit()