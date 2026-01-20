# OSRS Grand Exchange Portfolio Application - High-Level Design

## Overview

Transform the existing OSRS GE data aggregation system into a "stock portfolio" style application with a modern Vue.js frontend, professional charting, and portfolio management features.

### Design Decisions
- **User Scope**: Single user initially, architected for future multi-user support
- **MVP Focus**: Portfolio management + TradingView charts
- **Real-time Strategy**: Polling every 30-60 seconds (matches backend 60s refresh)
- **Phase 2 Features**: Watchlists, alerts, multi-user auth

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Vue.js SPA (Vite + TypeScript)              │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────┐  │
│  │  Portfolio   │ │  Watchlist   │ │  Charts (TradingView)  │  │
│  │  Dashboard   │ │  Manager     │ │  Lightweight Charts    │  │
│  └──────────────┘ └──────────────┘ └────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │         shadcn-vue + Tailwind CSS + Pinia + Vue Query      ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  /api/items  │  /api/portfolio  │  /api/watchlist  │  /api/alerts│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SQLite Database          │  Background Services                 │
│  - item (existing)        │  - Data backend (existing 60s)   │
│  - itemsnapshot (existing)│  - Alert Processor (future)         │
│  - portfolio (new)        │                                      │
│  - portfolio_holding (new)│                                      │
│  - transaction (new)      │                                      │
│  - watchlist (new)        │                                      │
│  - alert (new)            │                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## New Database Schema

### Portfolio Tables

```sql
-- Portfolio container
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL DEFAULT 'Main Portfolio',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual holdings
CREATE TABLE portfolio_holding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolio(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES item(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    avg_entry_price REAL NOT NULL,  -- Cost basis per unit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, item_id)
);

-- Transaction history (buy/sell audit trail)
CREATE TABLE transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolio(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES item(id),
    transaction_type VARCHAR(10) NOT NULL CHECK(transaction_type IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    price_per_unit REAL NOT NULL,
    total_value REAL NOT NULL,  -- quantity * price_per_unit
    ge_tax REAL DEFAULT 0,      -- Tax paid on sells (1%, max 5M)
    notes TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watchlists (future)
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL DEFAULT 'My Watchlist',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE watchlist_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_id INTEGER NOT NULL REFERENCES watchlist(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES item(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(watchlist_id, item_id)
);

-- Price alerts (future)
CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES item(id),
    alert_type VARCHAR(20) NOT NULL CHECK(alert_type IN ('PRICE_ABOVE', 'PRICE_BELOW', 'MARGIN_ABOVE', 'VOLUME_ABOVE')),
    threshold REAL NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_portfolio_holding_portfolio ON portfolio_holding(portfolio_id);
CREATE INDEX idx_portfolio_holding_item ON portfolio_holding(item_id);
CREATE INDEX idx_transaction_portfolio ON transaction(portfolio_id);
CREATE INDEX idx_transaction_item ON transaction(item_id);
CREATE INDEX idx_transaction_date ON transaction(executed_at);
CREATE INDEX idx_watchlist_item_watchlist ON watchlist_item(watchlist_id);
CREATE INDEX idx_alert_item ON alert(item_id);
CREATE INDEX idx_alert_active ON alert(is_active);
```

### SQLModel Definitions

```python
# backend/models/portfolio_models.py

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class AlertType(str, Enum):
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    MARGIN_ABOVE = "MARGIN_ABOVE"
    VOLUME_ABOVE = "VOLUME_ABOVE"

class Portfolio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Main Portfolio", max_length=100)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    holdings: list["PortfolioHolding"] = Relationship(back_populates="portfolio")
    transactions: list["Transaction"] = Relationship(back_populates="portfolio")

class PortfolioHolding(SQLModel, table=True):
    __tablename__ = "portfolio_holding"

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    quantity: int = Field(default=0)
    avg_entry_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    portfolio: Optional[Portfolio] = Relationship(back_populates="holdings")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    transaction_type: TransactionType
    quantity: int
    price_per_unit: float
    total_value: float
    ge_tax: float = Field(default=0)
    notes: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    portfolio: Optional[Portfolio] = Relationship(back_populates="transactions")

class Watchlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="My Watchlist", max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    items: list["WatchlistItem"] = Relationship(back_populates="watchlist")

class WatchlistItem(SQLModel, table=True):
    __tablename__ = "watchlist_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlist.id", index=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

    watchlist: Optional[Watchlist] = Relationship(back_populates="items")

class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    alert_type: AlertType
    threshold: float
    is_active: bool = Field(default=True)
    triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## API Endpoints

### Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/items` | List items with pagination & filtering |
| GET | `/api/items/{id}` | Get single item with current prices |
| GET | `/api/items/search?q={query}` | Fuzzy search by name |
| GET | `/api/items/{id}/history` | Historical OHLCV data for charts |
| GET | `/api/items/top-margins` | Top margin opportunities |
| GET | `/api/items/top-volume` | Highest volume items |

### Portfolio
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolios` | List all portfolios |
| POST | `/api/portfolios` | Create portfolio |
| GET | `/api/portfolios/{id}` | Get portfolio with holdings & P&L |
| PUT | `/api/portfolios/{id}` | Update portfolio metadata |
| DELETE | `/api/portfolios/{id}` | Delete portfolio |
| GET | `/api/portfolios/{id}/holdings` | List holdings |
| POST | `/api/portfolios/{id}/holdings` | Add/update holding |
| DELETE | `/api/portfolios/{id}/holdings/{holding_id}` | Remove holding |
| GET | `/api/portfolios/{id}/transactions` | Transaction history |
| POST | `/api/portfolios/{id}/transactions` | Record transaction |
| GET | `/api/portfolios/{id}/performance` | P&L breakdown |

### Watchlist (Future)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/watchlists` | List watchlists |
| POST | `/api/watchlists` | Create watchlist |
| GET | `/api/watchlists/{id}` | Get watchlist with items |
| DELETE | `/api/watchlists/{id}` | Delete watchlist |
| POST | `/api/watchlists/{id}/items` | Add item |
| DELETE | `/api/watchlists/{id}/items/{item_id}` | Remove item |

### Alerts (Future)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | List alerts |
| POST | `/api/alerts` | Create alert |
| PUT | `/api/alerts/{id}` | Update alert |
| DELETE | `/api/alerts/{id}` | Delete alert |
| GET | `/api/alerts/triggered` | Recently triggered alerts |

---

## API Response Schemas

### Portfolio Responses

```python
# api/schemas/portfolio.py

from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional

class HoldingResponse(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    avg_entry_price: float
    current_price: float

    @computed_field
    @property
    def total_cost(self) -> float:
        return self.quantity * self.avg_entry_price

    @computed_field
    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price

    @computed_field
    @property
    def unrealized_pnl(self) -> float:
        return self.current_value - self.total_cost

    @computed_field
    @property
    def unrealized_pnl_percent(self) -> float:
        if self.total_cost == 0:
            return 0
        return (self.unrealized_pnl / self.total_cost) * 100

class PortfolioSummaryResponse(BaseModel):
    id: int
    name: str
    total_value: float
    total_cost: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    realized_pnl: float
    holdings_count: int

class PortfolioDetailResponse(PortfolioSummaryResponse):
    holdings: list[HoldingResponse]
    recent_transactions: list["TransactionResponse"]

class TransactionResponse(BaseModel):
    id: int
    item_id: int
    item_name: str
    transaction_type: str
    quantity: int
    price_per_unit: float
    total_value: float
    ge_tax: float
    executed_at: datetime
```

### Chart Data

```python
class ChartDataPoint(BaseModel):
    timestamp: int  # Unix timestamp in seconds (TradingView format)
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None
```

---

## Frontend Architecture

### Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── components.json              # shadcn-vue config
│
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   │
│   ├── assets/
│   │   └── styles/
│   │       ├── globals.css
│   │       └── variables.css
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn-vue components
│   │   │   ├── button/
│   │   │   ├── card/
│   │   │   ├── dialog/
│   │   │   ├── dropdown-menu/
│   │   │   ├── input/
│   │   │   ├── table/
│   │   │   ├── tabs/
│   │   │   └── ...
│   │   │
│   │   ├── charts/
│   │   │   ├── PriceChart.vue        # TradingView Lightweight
│   │   │   ├── PortfolioChart.vue    # Portfolio value over time
│   │   │   ├── VolumeChart.vue       # Volume bars
│   │   │   └── MiniSparkline.vue     # Small inline charts
│   │   │
│   │   ├── portfolio/
│   │   │   ├── PortfolioCard.vue
│   │   │   ├── HoldingRow.vue
│   │   │   ├── TransactionForm.vue
│   │   │   ├── TransactionHistory.vue
│   │   │   └── PnLDisplay.vue
│   │   │
│   │   ├── items/
│   │   │   ├── ItemSearch.vue
│   │   │   ├── ItemCard.vue
│   │   │   ├── ItemTable.vue
│   │   │   └── TopMargins.vue
│   │   │
│   │   └── layout/
│   │       ├── AppHeader.vue
│   │       ├── AppSidebar.vue
│   │       └── PageContainer.vue
│   │
│   ├── composables/
│   │   ├── useItems.ts
│   │   ├── usePortfolio.ts
│   │   ├── useChart.ts
│   │   └── useFormatters.ts
│   │
│   ├── stores/
│   │   ├── index.ts
│   │   ├── portfolio.ts
│   │   ├── items.ts
│   │   └── ui.ts
│   │
│   ├── api/
│   │   ├── client.ts            # Axios instance
│   │   ├── items.ts
│   │   └── portfolio.ts
│   │
│   ├── types/
│   │   ├── item.ts
│   │   ├── portfolio.ts
│   │   └── chart.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts        # Price formatting (1k, 1m, etc.)
│   │   ├── calculations.ts      # P&L, margins, etc.
│   │   └── constants.ts
│   │
│   └── views/
│       ├── DashboardView.vue    # Main dashboard
│       ├── PortfolioView.vue    # Portfolio detail
│       ├── ItemView.vue         # Single item with chart
│       └── ExplorerView.vue     # Item browser/search
│
└── public/
    └── favicon.ico
```

### Key Views

**Dashboard View**
- Portfolio summary cards (total value, P&L)
- Top holdings performance
- Market overview (top margins, volume leaders)

**Portfolio View**
- Holdings table with real-time prices
- Add/remove holdings
- Transaction history
- P&L breakdown (realized vs unrealized)

**Item View**
- TradingView candlestick chart
- Item metadata and stats
- Quick actions (add to portfolio)

**Explorer View**
- Advanced item search and filtering
- Sortable data table

### TradingView Lightweight Charts Integration

```typescript
// composables/useChart.ts
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';

export function useChart(container: Ref<HTMLElement | null>) {
  const chart = ref<IChartApi | null>(null);
  const candleSeries = ref<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeries = ref<ISeriesApi<'Histogram'> | null>(null);

  const initChart = () => {
    if (!container.value) return;

    chart.value = createChart(container.value, {
      layout: {
        background: { color: '#0f172a' },  // Dark theme
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      width: container.value.clientWidth,
      height: 400,
    });

    candleSeries.value = chart.value.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    volumeSeries.value = chart.value.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
  };

  const setData = (data: CandlestickData[]) => {
    candleSeries.value?.setData(data);
  };

  return { chart, initChart, setData };
}
```

### shadcn-vue Components to Use

**Essential:**
- Button, Input, Label - Form elements
- Card - Container components
- Table - Holdings, transactions, items
- Dialog, Sheet - Modals and slide-overs
- Dropdown Menu - Actions menus
- Tabs - View switching
- Badge - Status indicators
- Skeleton - Loading states
- Toast - Notifications
- Command - Search palette (Cmd+K)

**Advanced:**
- Select, Combobox - Item selection
- Progress - Loading indicators
- Alert - Important messages

---

## Core Feature Implementation

### P&L Calculation

```python
def calculate_holding_pnl(holding: PortfolioHolding, current_price: float) -> dict:
    """Calculate unrealized P&L for a holding."""
    cost_basis = holding.quantity * holding.avg_entry_price
    current_value = holding.quantity * current_price
    unrealized_pnl = current_value - cost_basis

    return {
        "cost_basis": cost_basis,
        "current_value": current_value,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_pnl_percent": (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
    }

def calculate_sell_pnl(holding: PortfolioHolding, sell_price: float, quantity: int) -> dict:
    """Calculate realized P&L for a sell transaction including GE tax."""
    cost_basis = quantity * holding.avg_entry_price
    gross_proceeds = quantity * sell_price
    ge_tax = min(gross_proceeds // 100, 5_000_000)  # 1% capped at 5M
    net_proceeds = gross_proceeds - ge_tax
    realized_pnl = net_proceeds - cost_basis

    return {
        "cost_basis": cost_basis,
        "gross_proceeds": gross_proceeds,
        "ge_tax": ge_tax,
        "net_proceeds": net_proceeds,
        "realized_pnl": realized_pnl,
    }
```

### Chart Data Transformation

```python
# api/routers/items.py

@router.get("/{item_id}/history")
async def get_item_history(
    item_id: int,
    timeframe: str = "1D",  # 1H, 4H, 1D, 1W
    limit: int = 100,
    session: Session = Depends(get_session)
) -> list[ChartDataPoint]:
    """Get OHLCV data for TradingView charts."""

    intervals = {
        "1H": timedelta(hours=1),
        "4H": timedelta(hours=4),
        "1D": timedelta(days=1),
        "1W": timedelta(weeks=1),
    }
    interval = intervals.get(timeframe, timedelta(days=1))

    # Fetch snapshots from itemsnapshot table
    snapshots = session.exec(
        select(ItemSnapshot)
        .where(ItemSnapshot.item_id == item_id)
        .order_by(ItemSnapshot.timestamp.desc())
        .limit(limit * 12)
    ).all()

    # Group into OHLCV candles
    candles = aggregate_to_ohlcv(snapshots, interval)

    return [
        ChartDataPoint(
            timestamp=int(c["timestamp"].timestamp()),
            open=c["open"],
            high=c["high"],
            low=c["low"],
            close=c["close"],
            volume=c["volume"]
        )
        for c in candles[-limit:]
    ]
```

---

## Technology Stack

### Backend (extend existing)

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.13+ |
| Web Framework | FastAPI | 0.115+ |
| ORM | SQLModel | 0.0.24+ |
| Validation | Pydantic | 2.11+ |
| Database | SQLite | 3.x |
| Async HTTP | httpx | 0.27+ |

### Frontend (new)

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Vue.js | 3.5+ |
| Build Tool | Vite | 6.0+ |
| Language | TypeScript | 5.6+ |
| UI Components | shadcn-vue | latest |
| CSS Framework | Tailwind CSS | 3.4+ |
| State Management | Pinia | 2.2+ |
| Data Fetching | TanStack Vue Query | 5.x |
| Charts | TradingView Lightweight Charts | 4.2+ |
| HTTP Client | Axios | 1.7+ |
| Icons | Lucide Vue | latest |
| Router | Vue Router | 4.4+ |

### Dependencies to Add

**pyproject.toml additions:**
```toml
dependencies = [
    # ... existing ...
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "httpx>=0.27.0",
    "python-multipart>=0.0.9",
]
```

**package.json:**
```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "@tanstack/vue-query": "^5.0.0",
    "axios": "^1.7.0",
    "lightweight-charts": "^4.2.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0",
    "lucide-vue-next": "^0.447.0",
    "radix-vue": "^1.9.0",
    "@vueuse/core": "^11.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0",
    "vue-tsc": "^2.1.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## Files to Create

### Backend
```
api/
├── __init__.py
├── main.py              # FastAPI entry point
├── config.py            # Configuration
├── deps.py              # Dependencies (get_session, etc.)
├── routers/
│   ├── __init__.py
│   ├── items.py
│   ├── portfolio.py
│   ├── watchlist.py     # Future
│   └── alerts.py        # Future
├── schemas/
│   ├── __init__.py
│   ├── item.py
│   ├── portfolio.py
│   └── alert.py
└── services/
    ├── __init__.py
    ├── portfolio_service.py
    └── pnl_calculator.py

backend/models/
└── portfolio_models.py  # New SQLModel definitions
```

### Frontend
```
frontend/                # Entire new Vue.js project
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `pyproject.toml` | Add FastAPI, uvicorn, httpx dependencies |
| `backend/models/item_model.py` | Add relationships for portfolio joins |
| `backend/models/__init__.py` | Export new portfolio models |

---

## Implementation Phases

### MVP (Portfolio + Charts)

**Phase 1: API Foundation**
- Set up FastAPI application structure
- Create portfolio SQLModel models (portfolio, holding, transaction)
- Implement item endpoints (list, search, history for charts)
- Implement portfolio CRUD endpoints
- Database schema creation

**Phase 2: Frontend Setup**
- Initialize Vue.js + Vite + TypeScript project
- Configure Tailwind CSS and shadcn-vue
- Set up Pinia stores and Vue Query
- Create layout and navigation components
- Implement item search/browser

**Phase 3: Portfolio Features**
- Portfolio dashboard with summary cards
- Holdings table with real-time P&L
- Add/remove holdings UI
- Transaction recording and history
- P&L calculations (unrealized/realized)

**Phase 4: Charts**
- TradingView Lightweight Charts integration
- Item price history candlestick charts
- Volume overlay
- Timeframe selector (1H, 4H, 1D, 1W)
- Portfolio value over time chart

### Future (Phase 2 Release)

**Phase 5: Watchlists**
- Multiple named watchlists
- Quick add from item views
- Price change indicators

**Phase 6: Alerts & Multi-user**
- Price/margin/volume alerts
- Browser notifications
- User authentication (JWT)
- Multi-user data isolation

---

## Verification

1. **API Testing**: Run `pytest tests/api/` for endpoint tests
2. **Frontend Dev**: `cd frontend && pnpm dev` - verify UI at localhost:5173
3. **Integration**:
   - Start backend: `uvicorn api.main:app --reload`
   - Start frontend: `pnpm dev`
   - Test portfolio creation, adding holdings, viewing charts
4. **E2E Flow**: Create portfolio -> Add item -> View P&L -> Check chart

---

## References

- [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/)
- [shadcn-vue](https://www.shadcn-vue.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Pinia State Management](https://pinia.vuejs.org/)
- [TanStack Query (Vue)](https://tanstack.com/query/latest/docs/vue/overview)
