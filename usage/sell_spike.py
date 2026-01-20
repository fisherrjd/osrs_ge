# low price = insta sell

import streamlit as st
from api.models.item_model import Item
from api.models.item_volume_5m import ItemSnapshot
from sqlmodel import Session, create_engine, select

engine = create_engine("sqlite:///item_data.db")
session = Session(engine)


data_5m = session.exec(select(ItemSnapshot)).all()
data_latest = session.exec(select(ItemSnapshot)).all()

st.title("OSRS Item lookup")


# You can add more features like charts, tables, and filters here
