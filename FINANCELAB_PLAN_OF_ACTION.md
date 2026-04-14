# FinanceLab — Plan of Action (v2)
## From Spec to Working System · Phased Implementation
## Covers: Part 1 (Sections 1–30) + Tax Engine (A–J) + Part 2 (Sections 31–55)

**Date:** April 13, 2026
**Starting Point:** Phase 0 complete (infra running)
**Infrastructure:** Mac Mini M4 (local server)
**Spec Documents:**
- `FINANCELAB_COMPLETE_SYSTEM.md` — Sections 1–30 (core system)
- `FINANCELAB_TAX_ENGINE_COMPLETE.md` — Sections A–J (full tax engine)
- `FINANCELAB_COMPLETE_SYSTEM_PART2.md` — Sections 31–55 (advanced intelligence)

---

## Executive Assessment

Three spec documents totaling 55+ sections and 10 dedicated tax sections. The plan is now **8 phases** across ~30 weeks. Phases 0–5 cover the core system (Part 1). Phase 6 adds the full multi-country tax engine. Phases 7–8 cover advanced intelligence, ML, Apple integration, and edge infrastructure (Part 2).

**Core principle stays the same:** Every phase ends with something usable. No "infrastructure only" phases after Phase 0.

---

## Section Coverage Map

| Phase | Spec Sections Covered |
|-------|----------------------|
| 0 | 23 (infra setup) — **DONE** |
| 1 | 1, 2, 3, 4, 5, 6 (broker costs, basic tax, data, options, sentiment) |
| 2 | 9, 10, 12, 13, 15, 21 (GO/NO-GO, sizing, screener, earnings, alerts) |
| 3 | 7, 8, 14, 16, 17, 18, 23-AI (research, psychology, post-mortem, Ollama) |
| 4 | 11, 19, 22, 24, 25, 28 (web app, charts, cloud, backtesting) |
| 5 | 20, 26, 27, 29, 30 (multi-profile, security, monitoring, compliance) |
| 6 | Tax A–J, 46 (full tax engine, form generation) |
| 7 | 31–37, 39, 41–43 (alt data, vol surface, factors, geopolitical, arb) |
| 8 | 38, 44, 45, 47–55 (ML, NLQ, Apple, family office, edge CDN) |

---

## Phase 0 — Foundation (Week 1–2) ✅ COMPLETE

Mac Mini running. TimescaleDB + Redis live via Docker. Python venv active. yFinance, FRED fetchers working. FastAPI skeleton up. All delivered in `financelab_setup.sh`.

---

## Phase 1 — Personal Trading Intelligence (Week 2–4)

**Goal:** A working system that helps you make better trading decisions TODAY.

### 1A. Broker Cost Calculator (Section 1)
- `engines/broker_costs.py` — `calculate_true_cost()` function
- Support: Zerodha, Upstox, HDFC Sky, Angel One, IBKR
- All instrument types: equity delivery, intraday, futures, options (buy/sell), ITM expiry trap

### 1B. Basic Tax Intelligence (Section 2)
- `engines/tax_engine.py` — India STCG/LTCG detection with exact dates
- `when_to_sell_analysis()` — hold for LTCG?
- ITM option expiry STT trap calculator
- F&O turnover tracker (₹10Cr audit threshold alert)
- *Note: Full multi-country tax engine is Phase 6. This phase covers India equity/F&O basics only.*

### 1C. Data Pipeline (Section 6)
- `data/fetchers/` — modular fetchers for each source
  - `yfinance_fetcher.py` (no key needed, daily/hourly) — already built
  - `nse_fetcher.py` (option chain, FII/DII, announcements)
  - `fred_fetcher.py` (macro data) — already built
  - `finnhub_fetcher.py` (news, earnings calendar)
- `data/pipeline.py` — scheduled data ingestion
  - 08:00 IST: Pre-market data refresh
  - Every 5 min during market hours: Price updates
  - 18:00 IST: EOD FII/DII data, announcements

### 1D. Option Chain Intelligence (Section 3)
- `engines/option_chain.py`
  - Max pain calculator, PCR with interpretation
  - OI pattern detection (fresh long/short, unwinding, covering)
  - IV percentile calculation
- NSE option chain fetcher (session cookie method)

### 1E. News + Sentiment (Sections 4–5)
- `engines/sentiment.py`
  - FII/DII signal (highest weight — actual money flow)
  - FinBERT local sentiment (runs on M4 via MPS)
  - News source aggregation, weighted scoring

### 1F. FastAPI Backend
- REST endpoints for everything above
- `/api/cost-calculator`, `/api/tax/when-to-sell`, `/api/option-chain/{symbol}`, `/api/sentiment/{ticker}`, `/api/market/fii-dii`

### Deliverable
A running API you query before any trade. True cost, option chain analysis, sentiment, LTCG optimization — all answerable.

### Estimated time: 2–3 weeks

---

## Phase 2 — Decision Engine + Alerts (Week 4–6)

**Goal:** The system tells you what to do, not just shows you data.

### 2A. GO/NO-GO Signal Engine (Section 9)
- `engines/gonogo.py` — composite scoring 0–100
- Valuation + technical + fundamental + sentiment + option chain + macro + user thesis
- Configurable weights, clear signals: STRONG GO / GO / BORDERLINE / NO-GO / STRONG NO-GO
- True break-even price (all costs and taxes)

### 2B. Position Sizing (Section 10)
- `engines/position_sizing.py`
- Kelly Criterion (half-Kelly for safety), ATR-based volatility sizing
- Portfolio concentration checks

### 2C. Macro Regime Classifier (Section 15)
- `engines/macro.py` — four-regime model: Goldilocks / Reflation / Stagflation / Deflation
- Updated daily from FRED data, feeds into GO/NO-GO weights

### 2D. Earnings Intelligence (Section 13)
- `engines/earnings.py` — pre-earnings analysis, calendar tracking, strategy recommendations

### 2E. Telegram Alerts (Section 21)
- `alerts/telegram_bot.py`
- Stop loss (CRITICAL), ITM expiry trap 3:00 PM (CRITICAL), FII large flow (HIGH), VIX spike (HIGH), earnings approaching (MEDIUM), LTCG milestone (MEDIUM), morning scan (daily)

### 2F. Morning Scanner (Section 12)
- `engines/screener.py` — daily NIFTY 500 scan, top 5 to Telegram, unusual options activity

### Deliverable
Morning alerts with top ideas. GO/NO-GO score + position size before every trade. Stop loss and tax alerts fire automatically.

### Estimated time: 2–3 weeks

---

## Phase 3 — AI + Research + Learning (Week 6–9)

**Goal:** The system learns from you and helps you think better.

### 3A. Ollama + RAG Setup (Section 23, Phase 3)
- Ollama with llama3.1:8b + nomic-embed-text
- ChromaDB for vector storage
- Inject all three spec documents as RAG context

### 3B. Human-AI Research Collaboration (Section 8)
- `engines/research.py` — accept thesis, AI cross-references all data
- Supporting/contradicting evidence, thesis score, bull/base/bear scenarios
- Research journal in database

### 3C. Universal Security Master (Section 7)
- `engines/entity_resolution.py` — ISIN via OpenFIGI, multi-exchange mapping, ADR premium/discount

### 3D. Management Quality Tracker (Section 14)
- `engines/management.py` — promoter pledges, insider transactions, auditor changes, RPT flags
- Score 0–100 with grade A/B/C/D

### 3E. Psychology + Consistency Engine (Section 16)
- `engines/psychology.py` — pre-trade checklist, monthly consistency score, pattern detection

### 3F. Trade Post-Mortem (Section 17)
- `engines/post_mortem.py` — auto post-mortem on every close, Ollama root cause analysis, lessons database

### 3G. Tax Loss Harvesting Scanner (Section 18)
- `engines/tax_harvest.py` — scan for harvest opportunities, net benefit calculation
- India advantage: no wash sale rule

### Deliverable
Write a thesis, get AI pushback. Track psychology, learn from past trades, harvest tax losses.

### Estimated time: 3–4 weeks

---

## Phase 4 — Web App + Charts + Polish (Week 9–13)

**Goal:** Bloomberg-style interface accessible from anywhere.

### 4A. Next.js Web App (Section 25)
- Next.js 14 App Router, authentication (Supabase Auth or JWT)
- Dashboard: portfolio overview, daily P&L, pending signals
- Pages: Screener, Research Journal, Trade Log, Tax Dashboard, Settings

### 4B. Bloomberg-Style Charts (Section 22)
- ECharts: candlestick + volume + RSI, option chain overlay, dark theme (#131722)

### 4C. Supabase Cloud Layer (Section 24)
- TimescaleDB stays local for time-series, Supabase for user data, notes, portfolios

### 4D. Cloudflare Tunnel (Section 23, Phase 6)
- Expose local services securely, custom domain, zero-trust access

### 4E. Backtesting (Section 28)
- VectorBT integration, paper trading, performance comparison

### 4F. Portfolio Risk Dashboard (Section 11)
- Correlation matrix, stress testing (NIFTY -10%, -20%), Effective-N

### 4G. Long-Term Goals (Section 19)
- Retirement corpus tracker, Core/Satellite/Tactical allocation, SIP tracking

### Deliverable
Full web app accessible from anywhere. Charts, risk dashboards, research journal, backtesting.

### Estimated time: 4–5 weeks

---

## Phase 5 — Multi-Profile + Production Hardening (Week 13–16)

**Goal:** Family members can use it safely. Production-grade.

### 5A. Multi-Profile System (Section 20)
- Profile database, admin dashboard, trade review workflow, RLS in Supabase, per-profile encrypted credentials

### 5B. Security Hardening (Section 26)
- JWT + refresh tokens, AES-256 encryption, rate limiting, input validation

### 5C. Monitoring (Section 27)
- Health checks, uptime alerts, log aggregation, daily maintenance

### 5D. Regulatory Compliance (Section 29)
- Disclaimers, F&O turnover monitoring, US PDT rule, wash sale tracking

### 5E. Troubleshooting Automation (Section 30)
- Auto-recovery for NSE 401, Zerodha token refresh, Ollama cold start, disk/memory monitoring

### Deliverable
Multiple users, proper security, monitoring, compliance. Daily use by you and family.

### Estimated time: 3–4 weeks

---

## Phase 6 — Full Tax Engine (Week 16–21) 🆕

**Goal:** Complete multi-country tax system — from every transaction to cumulative tax bill to CA-ready export.

This is the big one from the Tax Engine spec. It turns the basic Phase 1B tax logic into a full-blown tax intelligence system.

### 6A. Universal Transaction Schema (Tax Spec Section A)
- `tax/models.py` — Master `Transaction` dataclass with 40+ fields
  - 30+ InstrumentType variants (India equity, F&O, MF, REIT, US equity/options, UK, EU, crypto, forex)
  - 20+ ActionType variants (buy, sell, dividend, bonus, split, exercise, ITM/OTM expiry, rollover, merger, spinoff)
  - CostBasisMethod: FIFO, LIFO, HIFO, Average, Specific ID, UK Section 104
  - 25+ TaxTreatment classifications across 5 countries
- `tax/models.py` — Portfolio (broker account) schema with per-portfolio tax config

### 6B. Broker Statement Import (Tax Spec Section A.3–A.4)
- `tax/importers/zerodha_pnl.py` — Parse Zerodha Tax P&L CSV
- `tax/importers/zerodha_fo.py` — Parse Zerodha F&O tradebook
- `tax/importers/ibkr.py` — Parse IBKR Activity Statement CSV
- `tax/importers/cdsl_cas.py` — Parse CDSL CAS PDF (cross-broker holdings)
- `tax/importers/manual.py` — Manual entry with full validation (quantity check, ITM STT warning, F&O audit threshold warning, FX rate validation)

### 6C. India Tax Engine — Complete (Tax Spec Section B)
- `tax/engines/india.py` — Full IndiaTaxEngine
  - FY 2024-25 rates: STCG 20%, LTCG 12.5% (₹1.25L exempt), F&O at slab, crypto 30% flat
  - Surcharge rates with LTCG/STCG cap at 15%
  - Auto-classify every transaction → TaxTreatment
  - Per-transaction tax calculation with grandfathering (Jan 31, 2018 FMV)
  - Loss Offset Engine — India's complex offset matrix:
    - STCG loss → can offset STCG + LTCG
    - LTCG loss → can offset LTCG only
    - F&O loss → business income only
    - Intraday → intraday only
    - Crypto → NOTHING (harshest rule)
  - Carry-forward periods (8yr equity/F&O, 4yr intraday, 0yr crypto)
  - Advance Tax Calculator (4 quarterly installments, 234B/234C penalty calculation)
  - F&O Turnover Calculator (ICAI guidelines, audit threshold)
  - STT + charges deduction tracker for F&O business income

### 6D. US Tax Engine — India Resident (Tax Spec Section C)
- `tax/engines/us.py` — IndiaResidentUSTaxEngine
  - DTAA India-USA: dividend withholding 25% (with W-8BEN), CG generally exempt at US end
  - India taxes gross US income, FTC for US withholding
  - Wash sale tracker (30-day window)
  - FBAR/FATCA check (not required for India residents' US accounts)

### 6E. UK Tax Engine (Tax Spec Section D)
- `tax/engines/uk.py` — UKSection104Pool
  - UK mandatory cost basis: Same-day rule → 30-day bed-and-breakfast rule → Section 104 pool
  - CGT rates: 18% basic / 24% higher, £3K annual exemption
  - IndiaResidentUKTaxEngine — India taxes UK gains, FTC for UK CGT paid

### 6F. European Tax Engines (Tax Spec Section E)
- `tax/engines/germany.py` — Abgeltungsteuer (25% + 5.5% soli = 26.375%), crypto exempt after 1yr, partial fund exemption
- `tax/engines/france.py` — PFU (30% flat), PEA exempt after 5yr
- `tax/engines/netherlands.py` — Box 3 deemed return system
- `tax/engines/eu_others.py` — Spain (19–28%), Italy (26%), Switzerland (0% private)

### 6G. DTAA Framework (Tax Spec Section F)
- `tax/dtaa.py` — Cross-border treaty rates
  - India-US, India-UK, India-Germany, India-France, India-Netherlands
  - Form 67 generator (Foreign Tax Credit claim)

### 6H. Cumulative Tax Bill Engine (Tax Spec Section G)
- `tax/cumulative.py` — The master engine
  - Aggregates ALL transactions across ALL portfolios across ALL countries
  - Real-time running tax liability dashboard
  - Per-portfolio tax summary breakdown
  - Tax Optimization Suggestions Engine:
    - "Hold INFY 23 more days → save ₹4,200 (STCG→LTCG)"
    - "Book ₹40K LTCG — still within ₹1.25L exemption"
    - "Harvest PAYTM loss ₹28K → save ₹5,600"
  - `what_if_sell_today()` — instant tax preview on any position

### 6I. CA Export Package (Tax Spec Section H)
- `tax/export.py` — Year-end Excel generator with 7 sheets:
  1. Tax Summary (total liability, TDS, advance tax, balance payable)
  2. All Transactions (every trade with tax classification)
  3. Schedule CG (STCG Part A + LTCG Part B for ITR)
  4. F&O Business Income (Schedule BP — turnover, expenses, audit check)
  5. Carry Forward Losses (with offset rules + deadlines)
  6. Foreign Income — Schedule FSI (US, UK, EU with FTC)
  7. Advance Tax Schedule (4 quarters + penalty calculation)

### 6J. Tax Form Generation (Part 2 Section 46)
- `tax/forms/itr_generator.py` — India ITR data prefill for CA
- Schedule CG, Schedule FSI, Schedule FA, Form 67 data

### 6K. Tax Dashboard UI Components (Tax Spec Section I)
- Transaction entry form (auto-calculate charges, instant tax preview, LTCG hold recommendation)
- Cumulative tax bill dashboard (running liability, advance tax schedule, per-portfolio breakdown)

### 6L. Tax Calendar + Alerts (Tax Spec Section J)
- India advance tax dates (Jun 15, Sep 15, Dec 15, Mar 15)
- ITR filing deadlines (Jul 31 / Oct 31)
- "File Form 67 before ITR" reminders
- "Book losses before March 31" alerts
- Telegram integration for all tax alerts

### Deliverable
Complete tax intelligence system. Import broker statements → auto-classify → calculate tax across 5 countries → generate CA-ready export. Real-time running tax bill. "What if I sell today?" on every position.

### Estimated time: 4–5 weeks

---

## Phase 7 — Alternative Data + Factor Models (Week 21–25) 🆕

**Goal:** Non-obvious data sources that give you an edge before official numbers.

### 7A. Alternative Data Engine (Section 31)
- `engines/alt_data/google_trends.py` — Brand search interest tracking (B2C companies)
- `engines/alt_data/job_postings.py` — Hiring velocity as growth proxy (LinkedIn, Glassdoor scraping)
- `engines/alt_data/import_export.py` — India import/export intelligence (leads official data by 1–2 months)
- `engines/alt_data/app_store.py` — App ratings/downloads for tech/fintech companies
- `engines/alt_data/aggregator.py` — Combine all alt data into single score per ticker

### 7B. Volatility Surface + Term Structure (Section 32)
- `engines/volatility.py` — Vol surface construction from option chain
- Skew analysis, term structure, NIFTY VIX analysis

### 7C. Market Microstructure (Section 33)
- `engines/microstructure.py` — Order book analysis, VWAP + market impact estimation

### 7D. Factor Model — Systematic Alpha (Section 34)
- `engines/factors.py` — Fama-French Five Factor Model
- Momentum factor, factor exposure analysis per stock

### 7E. Corporate Action Intelligence (Section 35)
- `engines/corporate_actions.py` — Track splits, bonuses, buybacks, mergers, spinoffs
- Auto-adjust cost basis on corporate actions

### 7F. Credit Analysis Engine (Section 36)
- `engines/credit.py` — Altman Z-Score, debt coverage ratios, credit risk scoring

### 7G. Geopolitical Risk Engine (Section 37)
- `engines/geopolitical.py` — Event impact mapping, country risk scoring
- Sector/ticker vulnerability assessment

### 7H. Sector Rotation Model (Section 39)
- `engines/sector_rotation.py` — Economic cycle sector clock, momentum-based rotation signals

### 7I. Insider Cluster Analysis (Section 41)
- `engines/insider.py` — Detect unusual insider buying/selling clusters across companies

### 7J. Short Squeeze Detector (Section 42)
- `engines/short_squeeze.py` — India short squeeze via F&O data (short interest proxy from futures OI)

### 7K. Arbitrage Scanner (Section 43)
- `engines/arbitrage.py` — Cash-futures arbitrage, pairs trading (India pairs like ICICI/HDFC, TCS/INFY)

### 7L. Dividend Intelligence (Section 40)
- `engines/dividends.py` — Dividend capture strategy, income tracking, yield forecasting

### Deliverable
Google Trends predicting earnings beats. Factor model explaining your returns. Corporate action auto-tracking. Arbitrage and squeeze alerts.

### Estimated time: 4–5 weeks

---

## Phase 8 — ML + NLQ + Apple + Ecosystem (Week 25–30) 🆕

**Goal:** Machine learning personalized to your data. Talk to your system in plain English. Full Apple ecosystem.

### 8A. Machine Learning Layer (Section 44)
- `ml/price_classifier.py` — XGBoost: "Will this stock beat NIFTY next 30 days?"
  - 50+ features: technical, fundamental, sentiment, options, macro
  - Trained on YOUR TimescaleDB data
- `ml/anomaly_detector.py` — Isolation Forest for unusual market activity before news
- `ml/personal_edge.py` — After 3+ months: where do YOU add alpha vs the AI signal?
  - Best hours, best days, best sectors, conviction level analysis

### 8B. Natural Language Query Interface (Section 38)
- `engines/nlq.py` — Ask questions in plain English
  - "What's my best performing sector this year?"
  - "Show me stocks with rising Google Trends and insider buying"
  - "How much tax if I sell RELIANCE today?"
- Ollama-powered query parsing → API calls → formatted response

### 8C. Apple Ecosystem Integration (Section 45)
- `apple/siri_shortcuts.py` — Siri integration via FastAPI endpoints
  - "Hey Siri, what's my portfolio?" → calls `/api/portfolio/summary`
  - "Hey Siri, market status?" → calls `/api/market/status`
- Apple Watch: compact complication showing daily P&L + top alert
- iPhone Widget: portfolio summary widget
- Apple Health bridge: sleep quality → FinanceLab (biometric trading bias detection)

### 8D. Trade Journaling With Emotion (Section 50)
- `engines/journal.py` — Log emotional + physical state with each trade
- Correlate: do you trade worse when stressed/tired/euphoric?
- Visualization: emotion heatmap vs returns

### 8E. Leading Indicators Network (Section 51)
- `engines/leading_indicators.py` — India early signals dashboard
- Cement dispatch, auto sales, power consumption, steel production → predict GDP

### 8F. Risk-Adjusted Performance Attribution (Section 52)
- `engines/attribution.py` — Brinson-Hood-Beebower attribution
- Alpha vs beta decomposition, sector allocation vs selection effect

### 8G. Content Creation Tools (Section 53)
- `engines/content.py` — Auto-generate shareable trade reports, portfolio summaries, market commentary via Ollama

### 8H. Competitive Intelligence (Section 48)
- `engines/competitive.py` — Company vs competitors comparison dashboard

### 8I. Insurance + Liability Integration (Section 47)
- `engines/liability.py` — Complete liability tracker alongside portfolio assets

### 8J. Family Office + Portfolio Consolidation (Section 49)
- `engines/family_office.py` — Consolidated view across all family members
- Combined tax optimization, portfolio-level correlation across families

### 8K. Regulatory Filing Tracker (Section 54)
- `engines/regulatory.py` — Monitor NSE/BSE filings, SEBI circulars, company announcements
- Alert on material regulatory changes affecting your holdings

### 8L. Edge CDN + Infrastructure (Section 55)
- Cloudflare Workers for edge-cached market data
- Cloudflare D1 for edge data (static reference data)
- Graceful degradation architecture (fallback chain if services fail)
- UPS + power continuity setup for Mac Mini

### Deliverable
ML models trained on your data. Talk to your system in English. Siri + Apple Watch integration. Family-wide portfolio consolidation. Full ecosystem.

### Estimated time: 5–6 weeks

---

## Updated Timeline Summary

| Phase | Focus | Weeks | Status |
|-------|-------|-------|--------|
| 0 | Foundation | 1–2 | ✅ DONE |
| 1 | Trading Intelligence | 2–4 | Ready to start |
| 2 | Decision Engine + Alerts | 4–6 | |
| 3 | AI + Research + Learning | 6–9 | |
| 4 | Web App + Charts | 9–13 | |
| 5 | Multi-Profile + Hardening | 13–16 | |
| 6 | Full Tax Engine | 16–21 | 🆕 |
| 7 | Alt Data + Factor Models | 21–25 | 🆕 |
| 8 | ML + NLQ + Apple + Ecosystem | 25–30 | 🆕 |

**Total: ~30 weeks (~7.5 months)**

---

## Critical Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| NSE API blocks scraping | Breaks option chain, FII/DII | Zerodha Kite as backup; paid NSE feed |
| Zerodha Kite API cost (₹2K/month) | Recurring expense | Start with yFinance + free APIs |
| Ollama slow on 8B model | Research/NLQ feels laggy | Keep warm; quantized 4-bit model |
| TimescaleDB disk fills fast | Database crash | Compression (7d) + retention (2yr) — already set |
| Single Mac Mini failure | Everything down | Docker auto-restart; UPS; Cloudflare tunnel auto-reconnect |
| FinBERT India accuracy | Bad sentiment signals | Validate against FII/DII flows; fine-tune |
| Tax rate changes (Budget) | Calculations wrong | Design tax rates as config, not hardcoded; annual update process |
| Broker CSV format changes | Import breaks | Version-aware parsers with format detection |
| ML model overfitting | False confidence | Walk-forward validation; minimum 50 trades before trusting personal edge |
| Apple API restrictions | Siri/Watch broken | Fallback to Telegram for all alerts |

---

## What NOT to Build (Yet)

- **Crypto trading** — Different market structure, different APIs. Only add if you actively trade
- **Forex via OANDA** — Add when you actually trade forex
- **Go-to-market / SaaS** — Build for yourself first, productize later
- **Advanced algo execution** — Spec correctly notes manual-execution only (no SEBI registration)
- **Real-time tick data** — 1-min data is enough; true tick data requires expensive feeds
- **Satellite imagery** — Listed in alt data spec but cost-prohibitive for personal use

---

## Recommended Phase 1 Order

Since Phase 0 is done, start Phase 1 in this order (each independently useful):

1. **Broker Cost Calculator** — pure logic, no external deps
2. **Data Pipeline + Fetchers** — extends what's already built
3. **Basic Tax Engine** — India equity/F&O only (full engine is Phase 6)
4. **Option Chain Intelligence** — depends on NSE fetcher
5. **Sentiment Engine** — depends on news fetcher + FinBERT install
6. **FastAPI endpoints** — wires it all together

---

## Spec Document Reference

| Document | Location | Sections |
|----------|----------|----------|
| Core System (Part 1) | `FINANCELAB_COMPLETE_SYSTEM.md` | 1–30 |
| Tax Engine | `FINANCELAB_TAX_ENGINE_COMPLETE.md` | A–J (10 sections) |
| Advanced Intelligence (Part 2) | `FINANCELAB_COMPLETE_SYSTEM_PART2.md` | 31–55 |

All three documents are in the project folder and should be injected into Ollama RAG when Phase 3 is built.
