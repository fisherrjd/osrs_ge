import streamlit as st
from sqlmodel import Session, select, create_engine
from aggregator.models.item_model import Item

engine = create_engine("sqlite:///item_data.db")
session = Session(engine)

st.title("OSRS Item lookup")

# Get all item names from the database
all_items = session.exec(select(Item)).all()
item_names = [item.item_name for item in all_items]

search_text = st.text_input("Fuzzy search item name:")

# Filter item names by search text (case-insensitive substring match)
if search_text:
    filtered_names = [
        name for name in item_names if search_text.lower() in name.lower()
    ]
else:
    filtered_names = item_names

selected_name = st.selectbox("Select item:", filtered_names)

if selected_name:
    statement = select(Item).where(Item.name == selected_name)
    item = session.exec(statement).first()
    if item:
        st.write(item)
    else:
        st.warning("Item not found.")

# You can add more features like charts, tables, and filters here
