# FinanceLab — Complete Requirements & Setup Guide

## System Overview

FinanceLab is a full-spectrum financial intelligence platform running on your Mac Mini.
It covers 13 asset categories across India and global markets with live data, trading signals,
tax computation, portfolio analytics, and 37 reference wiki articles.

---

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| macOS | 13+ (Ventura or later) | Host OS |
| Docker Desktop | 4.x | TimescaleDB + Redis containers |
| Python | 3.11+ | FastAPI backend |
| Node.js | 20+ LTS | Next.js frontend |
| npm | 10+ | Package management |
| Caddy | 2.x | Reverse proxy (optional) |
| cloudflared | latest | Cloudflare Tunnel for global access (optional) |
| Git | 2.x | Version control |

All prerequisites are auto-installed by `setup.sh`.

---

## Quick Start

```bash
# 1. Clone and enter the project
cd FinHubAI

# 2. Run full setup (installs everything)
chmod +x setup.sh && ./setup.sh

# 3. Edit API keys
nano .env

# 4. Start the server
./start.sh

# 5. Open browser
open http://localhost:3000
```

---

## Environment Variables (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (default: local TimescaleDB) |
| `REDIS_URL` | Yes | Redis connection string (default: local Redis) |
| `FINNHUB_API_KEY` | Optional | News & earnings data from Finnhub.io |
| `FRED_API_KEY` | Optional | Macro economic data from FRED |
| `NSE_COOKIES` | Optional | Browser cookie for NSE India API access |
| `SENTIMENT_FINBERT_ENABLED` | Optional | Enable FinBERT NLP sentiment (requires torch) |
| `CORS_ORIGINS` | Yes | Allowed CORS origins (default: localhost:3000) |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                   Caddy :8443               │
│              (reverse proxy)                 │
├──────────────────┬──────────────────────────┤
│  Next.js :3000   │   FastAPI :8000          │
│  (frontend)      │   (backend API)          │
├──────────────────┴──────────────────────────┤
│         TimescaleDB :5432                    │
│         Redis :6379                          │
│         (Docker containers)                  │
└─────────────────────────────────────────────┘
```

---

## Backend — Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ≥0.115 | Web framework |
| uvicorn | ≥0.32 | ASGI server |
| pydantic | ≥2.9 | Data validation |
| pydantic-settings | ≥2.6 | Environment config |
| sqlalchemy | ≥2.0 | ORM / database |
| psycopg | ≥3.2 | PostgreSQL driver |
| redis | ≥5.2 | Cache / session |
| httpx | ≥0.28 | HTTP client |
| yfinance | ≥0.2.50 | Market data (Yahoo Finance) |
| pandas | ≥2.2 | Data manipulation |
| numpy | ≥2.0 | Numerical computing |
| apscheduler | ≥3.10 | Scheduled data pipelines |
| scikit-learn | ≥1.5 | ML models |
| xgboost | ≥2.1 | Gradient boosting ML |
| openpyxl | ≥3.1 | Excel export for tax reports |
| ruff | ≥0.8 | Python linter |
| pytest | ≥8.3 | Testing framework |

---

## Frontend — Node.js Packages

| Package | Purpose |
|---------|---------|
| next 14.x | React framework (App Router) |
| react 18 | UI library |
| tailwindcss 3.x | Utility-first CSS |
| shadcn/ui | Component library (Radix-based) |
| lucide-react | Icon library |
| class-variance-authority | Variant styling |
| tailwind-merge | Class merging |

---

## API Endpoints (40+ routes)

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/health/deps` | Database + Redis status |

### Phase 1: Trading Intelligence
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/cost-calculator` | Broker cost calculation |
| POST | `/api/tax/when-to-sell` | STCG/LTCG hold analysis |
| GET | `/api/tax/itm-expiry-warning` | ITM option expiry STT trap |
| GET | `/api/tax/fo-turnover` | F&O audit threshold check |
| GET | `/api/option-chain/{symbol}` | NSE option chain analytics |
| GET | `/api/sentiment/{ticker}` | Composite sentiment score |
| GET | `/api/market/fii-dii` | FII/DII flow data |

### Phase 2: Decision Engine
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/gonogo/{symbol}` | GO/NO-GO composite signal (0-100) |
| GET | `/api/position-size/{symbol}` | ATR-based position sizing |
| POST | `/api/position-size/kelly` | Kelly criterion sizing |
| POST | `/api/portfolio/concentration` | Portfolio concentration check |
| GET | `/api/macro/regime` | Macro regime classification |
| GET | `/api/macro/dashboard` | Full FRED macro dashboard |
| GET | `/api/screener` | Morning scanner (top movers) |
| GET | `/api/earnings/{symbol}` | Earnings intelligence |

### Phase 3: Research & Analysis
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/research/thesis` | Thesis evaluation with scenarios |
| GET | `/api/management/{symbol}` | Management quality score (A-D) |

### Phase 4: Portfolio
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/portfolio/risk` | Portfolio risk + stress testing |
| POST | `/api/portfolio/retirement` | Retirement corpus projection |

### Phase 6: Advanced Tax
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tax/compute` | India multi-asset tax computation |
| POST | `/api/tax/us-india` | US tax for India residents (DTAA) |
| POST | `/api/tax/harvest-scan` | Tax-loss harvesting scanner |
| POST | `/api/tax/cumulative` | Cumulative tax bill + advance tax |

### Phase 7: Factor Analysis
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/factors/{symbol}` | Factor exposure (alpha, beta, momentum) |
| GET | `/api/factors/sectors/rotation` | Sector rotation momentum signals |
| GET | `/api/factors/credit/{symbol}` | Credit risk score |

### Markets
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/markets/categories` | All 13 market categories |
| GET | `/api/markets/pulse` | Global market pulse (17 instruments) |
| GET | `/api/markets/category/{cat}` | Full quotes for a category |
| GET | `/api/markets/gainers-losers/{cat}` | Top gainers/losers |
| GET | `/api/markets/quote/{symbol}` | Single instrument detail |
| GET | `/api/markets/search?q=` | Cross-category search |
| GET | `/api/markets/metals/india` | Gold/silver by 15 Indian cities |

### Wiki
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/wiki/categories` | 15 wiki categories |
| GET | `/api/wiki/articles` | All 37 articles (summary) |
| GET | `/api/wiki/category/{cat}` | Articles in a category |
| GET | `/api/wiki/search?q=` | Search articles |
| GET | `/api/wiki/article/{slug}` | Full article content |

---

## Web App Pages (17 pages)

| Route | Page | Phase |
|-------|------|-------|
| `/` | Dashboard — market pulse + feature grid | 1 |
| `/markets` | Markets hub — 13 categories, search, live quotes | 1 |
| `/markets/[symbol]` | Instrument detail — full quote info | 1 |
| `/markets/metals` | India gold/silver prices by city | 1 |
| `/screener` | Morning scanner — gainers, losers, volume | 2 |
| `/gonogo` | GO/NO-GO signal — composite score | 2 |
| `/cost` | Broker cost calculator — 5 brokers, 4 segments | 1 |
| `/tax` | Tax engine — India, US cross-border, cumulative | 1+6 |
| `/options` | Option chain analytics — max pain, PCR, OI | 1 |
| `/sentiment` | Sentiment analysis — FII/DII + news | 1 |
| `/portfolio` | Portfolio risk + retirement planner | 4 |
| `/research` | Research lab — thesis, management, earnings | 3 |
| `/wiki` | Wiki hub — 37 articles, search | - |
| `/wiki/[slug]` | Wiki article detail | - |
| `/settings` | Environment & API key guide | - |

---

## Market Coverage (13 Categories, 190+ Instruments)

| Category | Instruments | Examples |
|----------|-------------|---------|
| India Equity | 25 | Reliance, TCS, HDFC Bank, Infosys |
| India Mutual Funds | 8 | HDFC Flexi Cap, SBI Small Cap, ELSS |
| India Bonds | 4 | Liquid ETF, CPSE ETF, Bharat 22 |
| India Index | 3 | NIFTY 50, Bank NIFTY, SENSEX |
| Energy | 14 | WTI, Brent, Natural Gas, LNG, Gasoline |
| Commodities | 17 | Gold, Silver, Copper, Wheat, Coffee |
| Forex | 15 | USD/INR, EUR/USD, GBP/USD, DXY |
| US Equity | 30 | AAPL, MSFT, GOOGL, NVDA, AMZN |
| US Options | 9 | SPY, QQQ, IWM, AAPL, TSLA |
| Crypto | 15 | BTC, ETH, SOL, XRP, ADA |
| US Bonds | 12 | 10Y Yield, TLT, BND, HYG |
| US Futures | 10 | ES, NQ, YM, RTY, ZB, ZN |
| Real Estate | 16 | VNQ, AMT, PLD, Embassy REIT, Mindspace |

---

## Backend Engines (15 modules)

| Engine | File | Key Functions |
|--------|------|---------------|
| Broker Costs | `broker_costs.py` | `calculate_true_cost()` — 5 brokers, 4 segments |
| Tax (Basic) | `tax_engine.py` | `when_to_sell_analysis()`, ITM STT, F&O turnover |
| Tax (Advanced) | `tax_advanced.py` | India multi-asset, US-India DTAA, harvest, cumulative |
| Option Chain | `option_chain.py` | Max pain, PCR, OI heuristic, IV percentile |
| Sentiment | `sentiment.py` | FII/DII + news keywords + optional FinBERT |
| GO/NO-GO | `gonogo.py` | Composite 0-100 score, 6-factor weighted |
| Position Sizing | `position_sizing.py` | Kelly criterion, ATR-based, concentration check |
| Macro Regime | `macro.py` | 4-regime model (Goldilocks/Reflation/Stagflation/Deflation) |
| Screener | `screener.py` | NIFTY 50 scan, gainers/losers/unusual volume |
| Earnings | `earnings.py` | Pre-earnings analysis, strategy hints |
| Research | `research.py` | Thesis evaluation, bull/base/bear scenarios |
| Management | `management.py` | Governance score A-D, insider/institutional tracking |
| Portfolio | `portfolio.py` | Risk/correlation/stress + retirement planner |
| Factors | `factors.py` | Alpha/beta, sector rotation, credit score |
| Markets | `markets.py` | Global pulse, category overview, search |

---

## Data Sources

| Source | Type | Cost | Used For |
|--------|------|------|----------|
| Yahoo Finance (yfinance) | REST/scrape | Free | All market prices, fundamentals |
| FRED | REST API | Free (key required) | Macro indicators, yields |
| Finnhub | REST API | Free tier (60 calls/min) | News, earnings calendar |
| NSE India | REST/scrape | Free (cookie required) | Option chain, FII/DII |

---

## Wiki Coverage (37 Articles, 15 Categories)

| Category | Articles |
|----------|---------|
| India Equity | 4 (overview, large cap, intraday, STT) |
| India Mutual Funds | 3 (overview, ELSS, index funds) |
| India Bonds | 2 (overview, taxation) |
| India F&O | 3 (futures, options, option chain reading) |
| India Metals | 1 (city-wise gold/silver pricing) |
| Energy | 4 (crude, natural gas/LNG, refined, ETFs) |
| Commodities | 3 (precious metals, base metals, agriculture) |
| Forex | 3 (overview, USD/INR, DXY) |
| US Equity | 2 (overview, investing from India) |
| US Options | 1 (overview, 0DTE, VIX) |
| Crypto | 2 (overview, Bitcoin) |
| US Bonds | 2 (treasuries, bond ETFs) |
| US Futures | 1 (ES, NQ, micro contracts) |
| Real Estate | 2 (US REITs, India REITs) |
| Trading Concepts | 4 (broker costs, STCG/LTCG, FII/DII, sentiment) |

---

## Tax Engine Coverage

| Jurisdiction | Tax Types |
|-------------|-----------|
| India — Equity | STCG 20%, LTCG 12.5% (₹1.25L exemption) |
| India — F&O | Business income at slab rate |
| India — Intraday | Speculative income at slab rate |
| India — Crypto | 30% flat, no loss offset |
| India — Debt MF | Slab rate (post Apr 2023) |
| US — India Resident | DTAA benefit, 25% dividend withholding, FTC |
| Cumulative | Aggregate all transactions, advance tax schedule |
| Tax-Loss Harvesting | Scan for harvest opportunities (no wash-sale in India) |

---

## Shell Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | Install ALL prerequisites from scratch | `chmod +x setup.sh && ./setup.sh` |
| `start.sh` | Boot the entire stack (Docker, backend, frontend, Caddy) | `./start.sh` |

### What `setup.sh` installs:
1. Homebrew (if not present)
2. Docker Desktop (if not present)
3. Python 3.11+ (if not present)
4. Node.js 20+ (if not present)
5. Caddy reverse proxy
6. cloudflared (Cloudflare Tunnel)
7. Git
8. Creates `.env` from template
9. Pulls and starts Docker containers
10. Creates Python venv + installs packages
11. Installs Node.js packages + builds Next.js
12. Runs backend tests
13. Verifies everything works

### What `start.sh` does:
1. Creates `.env` if missing
2. Starts Docker (TimescaleDB + Redis)
3. Waits for health checks
4. Activates Python venv + installs deps
5. Builds Next.js (first run)
6. Starts FastAPI on :8000
7. Starts Next.js on :3000
8. Starts Caddy on :8443 (if installed)
9. Prints status summary
10. Ctrl-C stops everything cleanly

---

## Cloudflare Tunnel (Global Access)

See `deploy/cloudflare-tunnel.md` for detailed setup. Summary:

```bash
cloudflared tunnel login
cloudflared tunnel create finhub
# Configure ingress in ~/.cloudflared/config.yml
cloudflared tunnel route dns finhub your-domain.com
cloudflared tunnel run finhub
```

---

## Testing

```bash
# Backend tests
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v

# Frontend build check
cd web && npm run build

# API smoke test
curl http://localhost:8000/api/health
```

---

## Project Structure

```
FinHubAI/
├── setup.sh                 # Full environment setup
├── start.sh                 # Single-command launcher
├── docker-compose.yml       # TimescaleDB + Redis
├── .env.example             # Environment template
├── REQUIREMENTS.md          # This file
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings
│   ├── routes.py            # All 40+ API routes
│   ├── schemas.py           # Pydantic request/response models
│   ├── models.py            # SQLAlchemy database models
│   ├── db.py                # Database + Redis setup
│   ├── requirements.txt     # Python dependencies
│   ├── engines/             # Business logic (15 modules)
│   │   ├── broker_costs.py
│   │   ├── tax_engine.py
│   │   ├── tax_advanced.py
│   │   ├── option_chain.py
│   │   ├── sentiment.py
│   │   ├── gonogo.py
│   │   ├── position_sizing.py
│   │   ├── macro.py
│   │   ├── screener.py
│   │   ├── earnings.py
│   │   ├── research.py
│   │   ├── management.py
│   │   ├── portfolio.py
│   │   ├── factors.py
│   │   └── markets.py
│   └── data/
│       ├── wiki.py          # 37 reference articles
│       ├── pipeline.py      # Scheduled data ingestion
│       └── fetchers/        # Data source adapters
│           ├── markets_fetcher.py   # 190+ instruments
│           ├── yfinance_fetcher.py
│           ├── nse_fetcher.py
│           ├── finnhub_fetcher.py
│           └── fred_fetcher.py
├── web/
│   ├── app/                 # 17 Next.js pages
│   ├── components/          # Shared UI components
│   └── lib/                 # API utils + types
├── tests/                   # Backend test suite
└── deploy/
    ├── Caddyfile            # Reverse proxy config
    └── cloudflare-tunnel.md # Tunnel setup guide
```
