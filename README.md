# OSRS Grand Exchange Tracker

A real-time Old School RuneScape (OSRS) Grand Exchange price tracker and margin analyzer with interactive Streamlit dashboards.

## Overview

This project fetches live pricing data from the [OSRS Wiki API](https://prices.runescape.wiki/) and stores it in a local SQLite database. It provides multiple Streamlit-based interfaces to analyze trading opportunities, track margins, and monitor price movements.

## Features

### 📊 Data Aggregation
- **Real-time price updates**: Fetches latest buy/sell prices every 60 seconds
- **Volume tracking**: 24-hour and 5-minute volume data collection
- **Item mapping**: Complete item database with metadata (examine text, alch values, member status, trade limits)
- **SQLite storage**: Local database for historical analysis

### 🔍 Interactive Dashboards

#### 1. Margin Lookup (`usage/best_margin.py`)
Filter and sort items by trading margins with customizable criteria:
- Low/high price filters with operators (>, <)
- Margin thresholds for profit analysis
- Volume filtering to find liquid markets
- Auto-refreshing data every 60 seconds
- Human-readable number formats (1k, 1m, 1b, 1t)

#### 2. Item Lookup (`usage/item_lookup.py`)
Search and inspect individual items:
- Fuzzy search by item name
- Complete item details display
- Real-time price information

#### 3. Spike Detection (WIP)
- Buy spike detector (`usage/buy_spike.py`)
- Sell spike detector (`usage/sell_spike.py`)

## Data Models

### Item Model
Stores comprehensive item information:
- ID, name, examine text
- Low/high prices with timestamps
- 24-hour volume
- Alch values, trade limits
- Calculated margin property

### Volume Snapshots
5-minute interval price snapshots:
- Average high/low prices
- Volume data per price point
- Timestamp tracking

## Tech Stack

- **Python 3.13**
- **Streamlit**: Interactive web dashboards
- **SQLModel**: Database ORM with Pydantic validation
- **Requests**: API data fetching
- **Pytest**: Testing with coverage reports

## Setup

```bash
# Install dependencies using uv
uv sync

# Run the data aggregator (continuous updates)
python aggregator/db/data_input.py

# Launch a dashboard (in separate terminal)
streamlit run usage/best_margin.py
```

## Data Sources

All data is sourced from the [OSRS Wiki Prices API](https://prices.runescape.wiki/):
- `/api/v1/osrs/latest` - Latest buy/sell prices
- `/api/v1/osrs/mapping` - Item metadata
- `/api/v1/osrs/volumes` - 24-hour volumes
- `/api/v1/osrs/5m` - 5-minute price snapshots

## Project Structure

```
osrs_ge/
├── aggregator/          # Data collection & models
│   ├── db/              # Database operations
│   ├── models/          # SQLModel & Pydantic models
│   └── util/            # Helper functions (margin calc)
├── usage/               # Streamlit dashboards
├── tests/               # Pytest suite
└── .github/workflows/   # CI/CD configuration
```

## Use Cases

- **Flipping**: Find high-margin items with good volume
- **Market analysis**: Track price trends and spikes
- **Item research**: Quick lookup of item stats and prices
- **Arbitrage**: Identify trading opportunities

## License

This project uses data from the [OSRS Wiki](https://oldschool.runescape.wiki/) under their API terms.
