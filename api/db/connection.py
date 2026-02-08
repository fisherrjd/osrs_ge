"""
Shared database connection module.

This module provides database engines for use by routers and other components.
The actual data population is handled by cron jobs in api/data/.
"""

import os

from sqlmodel import SQLModel, create_engine

# Item data database (prices, snapshots, alerts)
ITEM_DB_FILE = os.getenv("DB_FILE", "sqlite:///item_data.db")
item_engine = create_engine(ITEM_DB_FILE)

# News data database (separate from item data)
NEWS_DB_FILE = os.getenv("NEWS_DB_FILE", os.getenv("DB_FILE", "sqlite:///news.db"))
news_engine = create_engine(NEWS_DB_FILE)

# Import all models to register them with SQLModel metadata
from api.schemas.item_model import Item  # noqa: E402, F401
from api.schemas.item_volume_5m import ItemSnapshot  # noqa: E402, F401
from api.schemas.dump_event import DumpEvent  # noqa: E402, F401
from api.schemas.news_models import NewsItem  # noqa: E402, F401

# Create all tables
SQLModel.metadata.create_all(item_engine)
SQLModel.metadata.create_all(news_engine)
