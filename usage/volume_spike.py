import streamlit as st
from streamlit_autorefresh import st_autorefresh

from sqlmodel import Session, select, create_engine
from aggregator.models.item_volume_5m import ItemSnapshot
from aggregator.models.item_model import Item
from datetime import datetime, timezone
from collections import defaultdict
import pandas as pd


REFRESH_INTERVAL = 60
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="db_refresh")

engine = create_engine("sqlite:///item_data.db")

st.title("OSRS Dump Tracker")


# Parse for 1k 1m etc values
def parse_num(val):
    if isinstance(val, (int, float)):
        return val
    val = str(val).replace(",", "").strip().lower()
    if val.endswith("k"):
        return int(float(val[:-1]) * 1_000)
    elif val.endswith("m"):
        return int(float(val[:-1]) * 1_000_000)
    try:
        return int(val)
    except ValueError:
        return 0


# User inputs
spike_levels = [10, 25, 50]
spike_level = st.selectbox("Spike Level (%)", spike_levels, index=0)
min_avg_volume = st.number_input(
    "Minimum average volume (cumulative)", min_value=0, value=1000, step=100
)
min_price = st.number_input(
    "Minimum price (avg_high_price)", min_value=0, value=1000, step=100
)
st.write(
    "Spike detection uses the cumulative average of all previous data for each item."
)

# Get items from the database each refresh
with Session(engine) as session:
    all_items = session.exec(select(ItemSnapshot)).all()
    all_item_objs = session.exec(select(Item)).all()

    item_snapshots = defaultdict(list)
    for snap in all_items:
        item_snapshots[snap.item_id].append(snap)

    spikes = []
    for item_id, snaps in item_snapshots.items():
        snaps_sorted = sorted(snaps, key=lambda x: x.timestamp)
        for i in range(1, len(snaps_sorted)):
            curr = snaps_sorted[i]
            prev_snaps = snaps_sorted[:i]
            if not prev_snaps:
                continue
            avg_volume = sum(s.total_volume for s in prev_snaps) / len(prev_snaps)
            if avg_volume == 0 or avg_volume < min_avg_volume:
                continue
            percent_increase = (curr.total_volume - avg_volume) / avg_volume * 100
            # Find price for this snapshot, fallback to previous non-null
            price = curr.avg_high_price
            if price is None:
                # fallback to last non-null price in prev_snaps
                for s in reversed(prev_snaps):
                    if s.avg_high_price is not None:
                        price = s.avg_high_price
                        break
            if price is None:
                continue  # skip if no price at all
            if price < min_price:
                continue
            spike_level_val = None
            for lvl in reversed(spike_levels):
                if percent_increase >= lvl:
                    spike_level_val = lvl
                    break
            if spike_level_val:
                # Find next price after spike
                next_price = None
                for future_snap in snaps_sorted[i + 1 :]:
                    if future_snap.avg_high_price is not None:
                        next_price = future_snap.avg_high_price
                        break
                price_drop = price - next_price if next_price is not None else None
                spikes.append(
                    {
                        "item_id": item_id,
                        "item_name": None,  # will fill later
                        "percent_increase": percent_increase,
                        "spike_level": spike_level_val,
                        "avg_volume": avg_volume,
                        "curr_volume": curr.total_volume,
                        "timestamp": curr.timestamp,
                        "price": price,
                        "price_drop": price_drop,
                    }
                )

    id_to_name = {item.id: item.item_name for item in all_item_objs}
    for s in spikes:
        s["item_name"] = id_to_name.get(s["item_id"], "Unknown")

    spikes_sorted = sorted(spikes, key=lambda x: x["percent_increase"], reverse=True)


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds} seconds ago"
    elif total_seconds < 3600:
        return f"{total_seconds // 60} minutes ago"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600} hours ago"
    else:
        return f"{total_seconds // 86400} days ago"


if spikes_sorted:
    df_spikes = pd.DataFrame(
        [
            {
                "Name": s["item_name"],
                "Percent Increase": f"{s['percent_increase']:.2f}%",
                # "Average Volume (2h)": int(s["avg_volume"]),
                # "Current Volume": s["curr_volume"],
                "Price": s["price"],
                "Price Drop After Spike": (
                    f"{s['price_drop']:.2f}" if s["price_drop"] is not None else "N/A"
                ),
                "Time Since Spike": format_timedelta(
                    datetime.now(timezone.utc)
                    - (
                        s["timestamp"].replace(tzinfo=timezone.utc)
                        if s["timestamp"].tzinfo is None
                        else s["timestamp"]
                    )
                ),
            }
            for s in spikes_sorted
            if s["spike_level"] == spike_level
        ]
    )
    st.subheader(f"Top Volume Spikes (Level: {spike_level}%)")
    st.dataframe(df_spikes)
else:
    st.warning("No volume spikes found matching criteria.")
