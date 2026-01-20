# Workflows and Processes

## Primary Workflows

### 1. Data Ingestion Workflow

**Purpose:** Continuously fetch and update market data from RuneScape Wiki API

**Frequency:** Every 60 seconds (5-minute intervals for snapshots)

**Entry Point:** `python -m backend.db.item_data`

```mermaid
flowchart TD
    Start([Start Main Loop]) --> Init[Initialize DB & Session]
    Init --> Fetch[fetch_all_data]

    Fetch --> API1[GET /osrs/mapping]
    Fetch --> API2[GET /osrs/latest]
    Fetch --> API3[GET /osrs/volumes]
    Fetch --> API4[GET /osrs/5m]

    API1 --> Val1[Validate MappingList]
    API2 --> Val2[Validate LatestData]
    API3 --> Val3[Validate Volume24h]
    API4 --> Val4[Validate Volume5m]

    Val1 --> Merge[Merge Data Sources]
    Val2 --> Merge
    Val3 --> Merge

    Merge --> Update[update_database]
    Update --> DB1[(Update Item Table)]

    Val4 --> Check{Run count % 5 == 0?}
    Check -->|Yes| SaveSnapshot[save_volume5m_to_db]
    Check -->|No| Print1[Print success message]
    SaveSnapshot --> DB2[(Insert ItemSnapshot)]
    DB2 --> Print2[Print snapshot saved]
    Print2 --> Sleep
    Print1 --> Sleep[Sleep 60 seconds]

    Sleep --> Increment[Increment run_count]
    Increment --> Fetch
```

**Detailed Steps:**

**Step 1: Initialization**
```python
engine = create_engine(DB_FILE)
session = Session(engine)
SQLModel.metadata.create_all(engine)
run_count = 0
```

**Step 2: Fetch All Data**
```python
mapping_data, latest_data, volume_data, volume_5m_data = fetch_all_data()
```

**Step 3: Update Item Table**
```python
mapping_dict = {item.id: item for item in mapping_data.items}
volume_dict = volume_data.data

for item_id, prices in latest_data.data.items():
    mapping_info = mapping_dict.get(item_id)
    if not mapping_info:
        continue

    volume_info = volume_dict.get(str(item_id), 0)

    item = Item(
        id=item_id,
        name=mapping_info.name,
        # ... all other fields
    )
    session.merge(item)  # Upsert

session.commit()
```

**Step 4: Save Volume Snapshots (Every 5th Run)**
```python
if run_count % 5 == 0:
    save_volume5m_to_db(volume_5m_data, engine)
    print("ItemVolume5m table updated!")
```

**Step 5: Wait and Repeat**
```python
print("Data saved successfully!")
print("Waiting 60 seconds for next run...")
run_count += 1
time.sleep(60)
```

**Error Handling:**
- API failures raise exceptions (crashes loop)
- No retry logic
- No graceful degradation

**Monitoring:**
- Console output for each successful run
- Special message for snapshot saves
- No logging framework

---

### 2. Best Margin Discovery Workflow

**Purpose:** Help users find profitable trading opportunities

**Entry Point:** `streamlit run usage/best_margin.py`

**User Interface Flow:**

```mermaid
flowchart TD
    Start([User Opens App]) --> Load[Load All Items from DB]
    Load --> Display[Display Filter Controls]

    Display --> Input1[Low Price Filter]
    Display --> Input2[High Price Filter]
    Display --> Input3[Margin Filter]
    Display --> Input4[Volume Filter]

    Input1 --> Parse1[parse_num]
    Input2 --> Parse2[parse_num]
    Input3 --> Parse3[parse_num]
    Input4 --> Parse4[parse_num]

    Parse1 --> Filter[Apply Filters]
    Parse2 --> Filter
    Parse3 --> Filter
    Parse4 --> Filter

    Filter --> Check{Items Found?}
    Check -->|Yes| Sort[Sort by Margin DESC]
    Check -->|No| Warn[Display Warning]

    Sort --> Table[Display DataFrame]
    Warn --> Wait
    Table --> Wait[Wait for Refresh]

    Wait -->|60 seconds| Load
    Wait -->|User Changes Filter| Filter
```

**Detailed Steps:**

**Step 1: Initialize and Query Database**
```python
engine = create_engine("sqlite:///item_data.db")
with Session(engine) as session:
    all_items = session.exec(select(Item)).all()
```

**Step 2: Accept User Input**
```python
low_price_op = st.selectbox("Low price operator", ["<", ">"])
low_price_val = st.text_input("Low price value", value="100b")
high_price_op = st.selectbox("High price operator", ["<", ">"])
high_price_val = st.text_input("High price value", value="100b")
margin_op = st.selectbox("Margin operator", [">", "<"])
margin_val = st.text_input("Margin value", value="100k")
volume_op = st.selectbox("Volume operator", [">", "<"])
volume_val = st.text_input("Volume value", value="0")
```

**Step 3: Parse Human-Readable Numbers**
```python
def parse_num(val):
    # Handles: 100k, 1.5m, 2b, etc.
    if val.endswith("k"): return int(float(val[:-1]) * 1_000)
    if val.endswith("m"): return int(float(val[:-1]) * 1_000_000)
    if val.endswith("b"): return int(float(val[:-1]) * 1_000_000_000)
    if val.endswith("t"): return int(float(val[:-1]) * 1_000_000_000_000)
    return int(val)
```

**Step 4: Filter Items**
```python
filtered_items = [
    item for item in all_items
    if compare(item.low, low_price_op, parse_num(low_price_val))
    and compare(item.high, high_price_op, parse_num(high_price_val))
    and compare(item.margin, margin_op, parse_num(margin_val))
    and compare(item.volume_24h, volume_op, parse_num(volume_val))
]
```

**Step 5: Display Results**
```python
if filtered_items:
    df = pd.DataFrame([{
        "Name": item.name,
        "Low": item.low,
        "High": item.high,
        "Margin": item.margin,
        "Volume": item.volume_24h,
    } for item in filtered_items])
    df = df.sort_values(by="Margin", ascending=False)
    st.dataframe(df)
else:
    st.warning("No items found matching criteria.")
```

**Auto-Refresh:**
```python
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="db_refresh")
```

---

### 3. Item Lookup Workflow

**Purpose:** Search for specific items and view their details

**Entry Point:** `streamlit run usage/item_lookup.py`

```mermaid
flowchart TD
    Start([User Opens App]) --> Load[Load All Items from DB]
    Load --> Extract[Extract Item Names]

    Extract --> Input[User Enters Search Text]
    Input --> Filter{Search Text Empty?}

    Filter -->|Yes| ShowAll[Show All Names]
    Filter -->|No| Fuzzy[Fuzzy Match on Name]

    ShowAll --> Dropdown[Display Dropdown]
    Fuzzy --> Dropdown

    Dropdown --> Select[User Selects Item]
    Select --> Query[Query Item by Name]

    Query --> Found{Item Found?}
    Found -->|Yes| Display[Display Item Details]
    Found -->|No| Warn[Display Warning]

    Display --> Input
    Warn --> Input
```

**Detailed Steps:**

**Step 1: Query All Items**
```python
all_items = session.exec(select(Item)).all()
item_names = [item.item_name for item in all_items]  # BUG: should be .name
```

**Step 2: Filter by Search Text**
```python
search_text = st.text_input("Fuzzy search item name:")

if search_text:
    filtered_names = [
        name for name in item_names
        if search_text.lower() in name.lower()
    ]
else:
    filtered_names = item_names
```

**Step 3: Select and Display**
```python
selected_name = st.selectbox("Select item:", filtered_names)

if selected_name:
    statement = select(Item).where(Item.name == selected_name)
    item = session.exec(statement).first()
    if item:
        st.write(item)
    else:
        st.warning("Item not found.")
```

**Known Issues:**
- References `item.item_name` instead of `item.name`
- No error handling for database query failures

---

### 4. Spike Detection Workflow (Planned)

**Purpose:** Identify abnormal price or volume changes for trading opportunities

**Status:** In development (incomplete implementation)

**Intended Flow:**

```mermaid
flowchart TD
    Start([User Opens Spike Detection App]) --> Query[Query ItemSnapshot Table]
    Query --> Group[Group by item_id]

    Group --> Analyze[Analyze Time Series]
    Analyze --> Calc1[Calculate Moving Averages]
    Analyze --> Calc2[Calculate Standard Deviations]

    Calc1 --> Detect{Spike Detected?}
    Calc2 --> Detect

    Detect -->|Yes| Alert[Highlight Item]
    Detect -->|No| Skip[Continue to Next]

    Alert --> Display[Display Spike Details]
    Skip --> Display

    Display --> Chart[Show Price/Volume Chart]
    Chart --> Start
```

**Planned Features:**
- Detect buy spikes (sudden increase in buy price/volume)
- Detect sell spikes (sudden increase in sell price/volume)
- Configurable sensitivity thresholds
- Historical chart visualization
- Alert system for significant opportunities

**Current Implementation Status:**
- `buy_spike.py` - Only a comment
- `sell_spike.py` - Basic database queries, no analysis logic

---

## Supporting Workflows

### Database Initialization

**When:** First run or after database deletion

**Process:**
```mermaid
flowchart TD
    Start([Application Starts]) --> Check{DB File Exists?}
    Check -->|No| Create[SQLModel.metadata.create_all]
    Check -->|Yes| Connect[Open Connection]

    Create --> Tables[Create Tables: item, itemsnapshot]
    Tables --> Connect
    Connect --> Ready[Ready for Operations]
```

**Code:**
```python
engine = create_engine("sqlite:///item_data.db")
SQLModel.metadata.create_all(engine)
```

---

### Nix Development Environment Setup

**Entry Point:** `nix develop` or `direnv allow`

**Process:**
```mermaid
flowchart TD
    Start([Developer Runs nix develop]) --> Fetch[Fetch Nix Dependencies]
    Fetch --> Build[Build UV Environment]

    Build --> Python[Install Python 3.13]
    Build --> Deps[Install Python Packages]
    Build --> Tools[Install Dev Tools]

    Python --> Link[Symlink UV Site Packages]
    Deps --> Link
    Tools --> Link

    Link --> Env[Set PYTHONPATH]
    Env --> Scripts[Expose CLI Scripts]

    Scripts --> Shell[Enter Development Shell]
```

**Available Scripts:**
- `black` - Code formatter
- `ruff` - Linter
- `ty` - Type checker
- `db` - Run data ingestion

---

### Testing Workflow (Historical)

**Note:** Test source files not in repository

**Inferred Structure:**
```mermaid
flowchart TD
    Start([Run pytest]) --> Discover[Discover Tests]

    Discover --> Unit1[Test Data Models]
    Discover --> Unit2[Test Item Model]
    Discover --> Unit3[Test ItemSnapshot]
    Discover --> Unit4[Test Margin Calc]
    Discover --> Unit5[Test Averages]
    Discover --> Int1[Test Data Input]
    Discover --> UI1[Test Best Margin]
    Discover --> UI2[Test Item Lookup]

    Unit1 --> Report[Generate Report]
    Unit2 --> Report
    Unit3 --> Report
    Unit4 --> Report
    Unit5 --> Report
    Int1 --> Report
    UI1 --> Report
    UI2 --> Report

    Report --> Coverage[Generate Coverage]
    Coverage --> HTML[htmlcov Directory]
```

**Test Categories:**
- **Unit Tests:** Models, utilities
- **Integration Tests:** Database operations
- **UI Tests:** Streamlit applications

---

## Operational Procedures

### Starting the System

**Step 1: Start Data Collection**
```bash
# Terminal 1
python -m backend.db.item_data
# Or with Nix:
db
```

**Step 2: Launch Web Interface**
```bash
# Terminal 2
streamlit run usage/best_margin.py

# Or other apps:
streamlit run usage/item_lookup.py
```

### Stopping the System

**Data Collection:**
- Press `Ctrl+C` to stop the infinite loop
- Partial data updates are committed

**Web Interface:**
- Press `Ctrl+C` in terminal
- Streamlit handles graceful shutdown

### Database Maintenance

**Backup:**
```bash
cp item_data.db item_data.db.backup
```

**Reset:**
```bash
rm item_data.db
# Next run will recreate with fresh data
```

**Inspect:**
```bash
sqlite3 item_data.db
.tables
.schema item
SELECT COUNT(*) FROM item;
```

### Monitoring

**Check Data Freshness:**
```sql
SELECT name, datetime(highTime, 'unixepoch') as last_update
FROM item
ORDER BY highTime DESC
LIMIT 10;
```

**Check Snapshot Collection:**
```sql
SELECT COUNT(*) as snapshot_count,
       MIN(timestamp) as oldest,
       MAX(timestamp) as newest
FROM itemsnapshot;
```

**Find Profitable Items:**
```sql
SELECT name, low, high,
       (high - MAX(high / 100, 5000000) - low) as margin,
       volume_24h
FROM item
WHERE margin > 10000
  AND volume_24h > 1000
ORDER BY margin DESC
LIMIT 20;
```
