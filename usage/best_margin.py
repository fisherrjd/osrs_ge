import streamlit as st
from sqlmodel import Session, select, create_engine
from aggregator.models.item_model import Item

engine = create_engine("sqlite:///mydb.sqlite3")
session = Session(engine)

st.title("OSRS Margin lookup")


# Helper to parse values like '100k', '1m', etc.
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

low_price_op = st.selectbox("Low price operator", ["<", ">"],)
low_price_val = st.text_input("Low price value", value="100m")
high_price_op = st.selectbox("High price operator", ["<", ">"])
high_price_val = st.text_input("High price value", value="100m")
margin_op = st.selectbox("Margin operator", [">", "<"])
margin_val = st.text_input("Margin value", value="100k")
volume_op = st.selectbox("Volume operator", [">", "<"])
volume_val = st.text_input("Volume value", value="100")

# Get all items from the database
all_items = session.exec(select(Item)).all()

# Helper function for comparison
def compare(val, op, ref):
    return val > ref if op == ">" else val < ref

# Filter items based on user criteria
filtered_items = [
    item for item in all_items
    if compare(item.low, low_price_op, parse_num(low_price_val))
    and compare(item.high, high_price_op, parse_num(high_price_val))
    and compare(item.margin, margin_op, parse_num(margin_val))
    and compare(item.volume, volume_op, parse_num(volume_val))
]

if filtered_items:
    import pandas as pd
    df = pd.DataFrame([
        {
            "Name": item.item_name,
            "Low": item.low,
            "High": item.high,
            "Margin": item.margin,
            "Volume": item.volume
        }
        for item in filtered_items
    ])
    df = df.sort_values(by="Margin", ascending=False)  # Sort by Margin descending
    st.dataframe(df)
else:
    st.warning("No items found matching criteria.")
