# Codebase Information

## Project Overview
**Project Name:** OSRS Grand Exchange Tracker
**Repository:** osrs_ge
**Version:** 0.1.0
**Primary Language:** Python 3.13+

## Description
A real-time Old School RuneScape (OSRS) Grand Exchange price tracking and margin analysis tool. The application fetches live market data from the RuneScape Wiki API, stores it in a local SQLite database, and provides interactive Streamlit web interfaces for analyzing trading opportunities and profit margins.

## Statistics
- **Total Lines of Code:** ~412 Python LOC
- **Total Python Files:** 16
- **Primary Packages:** 2 (api, usage)
- **Test Coverage:** Test structure exists (source files not in repo)

## Repository Structure
```
osrs_ge/
├── api/          # Core data collection and models
│   ├── db/             # Database operations and API fetching
│   ├── models/         # SQLModel and Pydantic data models
│   └── util/           # Utility functions
├── usage/              # Streamlit web applications
├── tests/              # Test structure (bytecode only)
├── shared/             # Shared resources (currently empty)
├── default.nix         # Nix development environment
├── pyproject.toml      # Python project configuration
└── main.py             # Entry point

## Technology Stack
- **Language:** Python 3.13+
- **Database:** SQLite (SQLModel ORM)
- **Web Framework:** Streamlit
- **Data Validation:** Pydantic
- **HTTP Client:** requests
- **Development Tools:** black, ruff, ty
- **Build System:** hatchling
- **Environment Management:** uv, Nix

## Key Features
1. Real-time price data fetching from RuneScape Wiki API
2. Historical volume tracking (5-minute intervals)
3. Margin calculation with GE tax consideration
4. Interactive web dashboards for:
   - Finding best profit margins
   - Item lookup with fuzzy search
   - Volume spike detection (in development)
5. Auto-refreshing data display

## Development Environment
- Managed via Nix flake with custom package overlay
- UV-based Python environment management
- Integrated development scripts for database updates
- DuckDB available for data analysis
