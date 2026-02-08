from datetime import datetime, timezone

import requests
from sqlmodel import Session

from api.db.connection import item_engine as engine
from api.schemas.data_models import Volume5m
from api.schemas.item_volume_5m import ItemSnapshot
from api.services.spike_detector import run_detection_for_snapshots

VOLUME_5M_API_URL = "https://prices.runescape.wiki/api/v1/osrs/5m"

HEADERS = {
    "User-Agent": "@PapaBear#2007",
    "From": "dev@jade.rip",
}


def fetch_data(api_url) -> dict:
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def volume5m_wrapper() -> Volume5m:
    data = fetch_data(VOLUME_5M_API_URL)
    return Volume5m.model_validate(data)


def save_volume5m_to_db(volume_5m_data: Volume5m, engine):
    """Save Volume5m pydantic model data to ItemSnapshot SQLModel table and detect events."""
    now = datetime.now(timezone.utc)
    snapshots = []

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
            snapshots.append(record)
        session.commit()

        # Run spike/dump detection on the new snapshots
        events = run_detection_for_snapshots(session, snapshots)
        if events:
            for event in events:
                session.add(event)
            session.commit()
            print(f"Detected {len(events)} dump/spike events!")


if __name__ == "__main__":
    print("Fetching 5-minute volume data...")
    volume_5m_data = volume5m_wrapper()
    save_volume5m_to_db(volume_5m_data, engine)
    print("ItemVolume5m table updated!")
