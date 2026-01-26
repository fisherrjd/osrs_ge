# OSRS Portfolio Management Plan

## Overview
Build a user portfolio system that allows players to track their OSRS items, quantities, and value over time. Users can log in, manage their item collections, and see portfolio performance metrics.

## Features

### Core Features
- User authentication (login/register)
- Add/remove items to portfolio
- Track item quantities
- View current portfolio value
- Historical portfolio value tracking
- Profit/loss calculations
- Portfolio diversity metrics

### Advanced Features
- Multiple portfolios per user (e.g., "Main Account", "Ironman", "Merching")
- Portfolio sharing (public/private)
- Price alerts for portfolio items
- Export portfolio data (CSV/JSON)
- Portfolio comparison charts
- Transaction history log

## Architecture

### Backend (API)
- **User authentication**: JWT-based auth system
- **User management**: Registration, login, profile
- **Portfolio CRUD**: Create, read, update, delete portfolios
- **Portfolio items**: Add/remove/update items in portfolios
- **Value calculations**: Real-time and historical value tracking
- **Transaction logging**: Track all portfolio changes

### Frontend
- **Auth pages**: Login, register, password reset
- **Portfolio dashboard**: Overview of all portfolios
- **Portfolio detail view**: Individual portfolio with items
- **Add item modal**: Search and add items to portfolio
- **Charts**: Value over time, profit/loss graphs

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### Portfolios Table
```sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
```

### Portfolio Items Table
```sql
CREATE TABLE portfolio_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,  -- References existing items table
    quantity INTEGER NOT NULL DEFAULT 0,
    average_buy_price INTEGER,  -- Optional: user's avg buy price in GP
    notes TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE(portfolio_id, item_id)
);

CREATE INDEX idx_portfolio_items_portfolio_id ON portfolio_items(portfolio_id);
CREATE INDEX idx_portfolio_items_item_id ON portfolio_items(item_id);
```

### Portfolio Snapshots Table (Historical Tracking)
```sql
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    total_value INTEGER NOT NULL,  -- Total GP value
    item_count INTEGER NOT NULL,  -- Number of unique items
    snapshot_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

CREATE INDEX idx_portfolio_snapshots_portfolio_id ON portfolio_snapshots(portfolio_id);
CREATE INDEX idx_portfolio_snapshots_date ON portfolio_snapshots(snapshot_date);
```

### Transactions Table (Audit Log)
```sql
CREATE TABLE portfolio_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,  -- 'add', 'remove', 'update'
    quantity_change INTEGER NOT NULL,
    price_at_transaction INTEGER,  -- Item price at time of transaction
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX idx_portfolio_transactions_portfolio_id ON portfolio_transactions(portfolio_id);
CREATE INDEX idx_portfolio_transactions_created_at ON portfolio_transactions(created_at);
```

## Implementation Steps

### Phase 1: User Authentication
1. **Backend - Auth System**
   - Install dependencies: `passlib`, `python-jose[cryptography]`, `python-multipart`
   - Create user model (`api/models/user.py`)
   - Create auth utilities (`api/auth.py`)
     - Password hashing (bcrypt)
     - JWT token generation/validation
     - Get current user dependency
   - Create auth endpoints (`api/routes/auth.py`)
     - `POST /api/auth/register` - Register new user
     - `POST /api/auth/login` - Login (returns JWT)
     - `GET /api/auth/me` - Get current user info
     - `POST /api/auth/logout` - Logout (optional, client-side)

2. **Frontend - Auth UI**
   - Create auth store (`frontend/src/stores/auth.ts`)
     - Store JWT token in localStorage
     - Track logged-in state
     - User info management
   - Create auth pages
     - `LoginView.vue` - Login form
     - `RegisterView.vue` - Registration form
   - Create auth components
     - `AuthGuard.vue` - Protected route wrapper
   - Add route guards for protected pages
   - Add auth interceptor to axios for JWT headers

### Phase 2: Portfolio CRUD
1. **Backend - Portfolio Management**
   - Create portfolio model (`api/models/portfolio.py`)
   - Create portfolio service (`api/services/portfolio_service.py`)
     - Create/update/delete portfolios
     - Calculate portfolio values
     - Get portfolio statistics
   - Create portfolio endpoints (`api/routes/portfolios.py`)
     - `GET /api/portfolios` - List user's portfolios
     - `POST /api/portfolios` - Create new portfolio
     - `GET /api/portfolios/:id` - Get portfolio details
     - `PUT /api/portfolios/:id` - Update portfolio
     - `DELETE /api/portfolios/:id` - Delete portfolio
     - `GET /api/portfolios/:id/value` - Get current value
     - `GET /api/portfolios/:id/history` - Get value history

2. **Frontend - Portfolio Dashboard**
   - Create portfolio store (`frontend/src/stores/portfolio.ts`)
   - Create portfolio views
     - `PortfolioDashboard.vue` - List of all portfolios
     - `PortfolioDetail.vue` - Single portfolio view
     - `CreatePortfolio.vue` - Create new portfolio modal
   - Create portfolio components
     - `PortfolioCard.vue` - Portfolio summary card
     - `PortfolioStats.vue` - Stats display (value, P/L, etc.)

### Phase 3: Portfolio Items Management
1. **Backend - Items in Portfolio**
   - Create portfolio_item model (`api/models/portfolio_item.py`)
   - Create transaction model (`api/models/transaction.py`)
   - Update portfolio service with item operations
   - Create portfolio item endpoints
     - `GET /api/portfolios/:id/items` - List items in portfolio
     - `POST /api/portfolios/:id/items` - Add item to portfolio
     - `PUT /api/portfolios/:id/items/:item_id` - Update item quantity
     - `DELETE /api/portfolios/:id/items/:item_id` - Remove item
     - `GET /api/portfolios/:id/transactions` - Transaction history

2. **Frontend - Item Management**
   - Create item management components
     - `PortfolioItemList.vue` - List of items in portfolio
     - `PortfolioItemCard.vue` - Individual item display
     - `AddItemModal.vue` - Search and add items
     - `EditItemModal.vue` - Edit quantity/notes
   - Add item search functionality
   - Add quantity adjustment controls

### Phase 4: Value Tracking & Analytics
1. **Backend - Snapshots & Analytics**
   - Create snapshot model (`api/models/portfolio_snapshot.py`)
   - Create background job for daily snapshots
     - Run daily to capture portfolio values
     - Calculate based on current item prices
   - Add analytics endpoints
     - `GET /api/portfolios/:id/analytics` - Portfolio metrics
       - Total value
       - 24h change
       - 7d change
       - 30d change
       - Best/worst performers
       - Portfolio diversity score

2. **Frontend - Charts & Visualization**
   - Install chart library (Chart.js or Apache ECharts)
   - Create chart components
     - `PortfolioValueChart.vue` - Value over time line chart
     - `ItemDistributionChart.vue` - Pie/donut chart
     - `PerformanceChart.vue` - Item performance comparison
   - Add date range selector
   - Add profit/loss indicators

### Phase 5: Advanced Features
1. **Multiple Portfolios**
   - Portfolio selector dropdown
   - Quick switch between portfolios
   - Portfolio comparison view

2. **Transaction History**
   - Full audit log of changes
   - Filter by date, item, type
   - Export transaction history

3. **Sharing & Privacy**
   - Public/private toggle
   - Share link generation
   - Public portfolio view (no auth required)

4. **Price Alerts**
   - Set alerts for portfolio items
   - Notify when item hits target price
   - Email/in-app notifications

## API Authentication Flow

```
1. User registers/logs in
   → POST /api/auth/login { username, password }
   → Returns: { access_token, token_type: "bearer", user: {...} }

2. Frontend stores JWT in localStorage
   → authStore.setToken(access_token)

3. All protected requests include token
   → headers: { "Authorization": "Bearer <token>" }

4. Backend validates token on each request
   → Extracts user from JWT
   → Ensures user owns requested portfolio
```

## Security Considerations

### Password Security
- Use bcrypt for password hashing (cost factor: 12)
- Minimum password requirements (8+ chars, complexity)
- Rate limiting on auth endpoints
- Account lockout after failed attempts

### JWT Security
- Short expiration time (1-2 hours)
- Secure secret key (environment variable)
- Optional: Refresh token system
- Optional: Token blacklist for logout

### Authorization
- Verify user owns portfolio before operations
- Prevent users from accessing others' private portfolios
- Validate all input data
- SQL injection prevention (use parameterized queries)

### Rate Limiting
- Limit portfolio creation (e.g., 10 per user)
- Limit item additions (prevent spam)
- API rate limiting per user

## Frontend State Management

### Auth Store
```typescript
{
  token: string | null,
  user: User | null,
  isAuthenticated: boolean,
  login(username, password),
  register(username, email, password),
  logout(),
  refreshUser()
}
```

### Portfolio Store
```typescript
{
  portfolios: Portfolio[],
  currentPortfolio: Portfolio | null,
  loading: boolean,
  fetchPortfolios(),
  createPortfolio(data),
  updatePortfolio(id, data),
  deletePortfolio(id),
  addItem(portfolioId, itemId, quantity),
  updateItem(portfolioId, itemId, quantity),
  removeItem(portfolioId, itemId)
}
```

## UI/UX Considerations

### Dashboard Layout
- Card grid for multiple portfolios
- Quick stats on each card (value, 24h change)
- Color coding (green = profit, red = loss)
- Empty state for new users

### Portfolio Detail
- Item list with sortable columns
  - Item name (with icon)
  - Quantity
  - Current price
  - Total value
  - 24h change
  - Actions (edit, remove)
- Total value prominently displayed
- Add item button (floating action button or header)

### Mobile Responsive
- Stack cards on mobile
- Drawer for item search
- Swipe actions for quick edit/delete
- Touch-friendly controls

## Testing Strategy

### Backend Tests
- Auth endpoint tests (login, register, token validation)
- Portfolio CRUD tests
- Item management tests
- Value calculation tests
- Authorization tests (prevent unauthorized access)

### Frontend Tests
- Auth flow tests
- Portfolio creation/editing
- Item addition/removal
- Chart rendering
- Route guard tests

## Future Enhancements
- Portfolio templates (common item sets)
- Import from RuneLite bank screenshot
- Portfolio goals/targets
- Social features (follow other portfolios)
- Leaderboards (most valuable, best performers)
- Mobile app (React Native/Flutter)
- Real-time price updates (WebSocket)
- Portfolio rebalancing suggestions
- Integration with OSRS Grand Exchange API
