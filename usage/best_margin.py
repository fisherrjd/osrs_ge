import streamlit as st
from streamlit_autorefresh import st_autorefresh

from sqlmodel import Session, select, create_engine
from aggregator.models.item_model import Item

REFRESH_INTERVAL = 60
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="db_refresh")

engine = create_engine("sqlite:///item_data.db")

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
    elif val.endswith("b"):
        return int(float(val[:-1]) * 1_000_000_000)
    elif val.endswith("t"):
        return int(float(val[:-1]) * 1_000_000_000_000)
    try:
        return int(val)
    except ValueError:
        return 0


# User inputs
low_price_op = st.selectbox("Low price operator", ["<", ">"])
low_price_val = st.text_input("Low price value", value="100b")
high_price_op = st.selectbox("High price operator", ["<", ">"])
high_price_val = st.text_input("High price value", value="100b")
margin_op = st.selectbox("Margin operator", [">", "<"])
margin_val = st.text_input("Margin value", value="100k")
volume_op = st.selectbox("Volume operator", [">", "<"])
volume_val = st.text_input("Volume value", value="0")

# Get items from the database each refresh
with Session(engine) as session:
    all_items = session.exec(select(Item)).all()


# Helper function for comparison
def compare(val, op, ref):
    return val > ref if op == ">" else val < ref


# Filter items
filtered_items = [
    item
    for item in all_items
    if compare(item.low, low_price_op, parse_num(low_price_val))
    and compare(item.high, high_price_op, parse_num(high_price_val))
    and compare(item.margin, margin_op, parse_num(margin_val))
    and compare(item.volume_24h, volume_op, parse_num(volume_val))
]

if filtered_items:
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "Name": item.name,
                "Low": item.low,
                "High": item.high,
                "Margin": item.margin,
                "Volume": item.volume_24h,
            }
            for item in filtered_items
        ]
    )
    df = df.sort_values(by="Margin", ascending=False)
    st.dataframe(df)
else:
    st.warning("No items found matching criteria.")
