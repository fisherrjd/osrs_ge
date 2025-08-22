import streamlit as st
from streamlit_autorefresh import st_autorefresh

from sqlmodel import Session, select, create_engine
from aggregator.models.item_model import Item

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="db_refresh")

engine = create_engine("sqlite:///mydb.sqlite3")

st.title("OSRS Margin lookup")


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
volume_op = st.selectbox("Volume operator", [">", "<"])
volume_val = st.text_input("Volume value", value="100")

# Get items from the database each refresh
with Session(engine) as session:
    all_items = session.exec(select(Item)).all()


# Helper function for comparison
def compare(val, op, ref):
    return val > ref if op == ">" else val < ref


# Filter items
filtered_items = [
    item for item in all_items if compare(item.volume, volume_op, parse_num(volume_val))
]

if filtered_items:
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "Name": item.item_name,
                "Volume": item.volume,
            }
            for item in filtered_items
        ]
    )
    st.dataframe(df)
else:
    st.warning("No items found matching criteria.")
