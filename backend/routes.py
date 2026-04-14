# ruff: noqa: E501
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.config import get_settings
from backend.data.fetchers import nse_fetcher
from backend.db import check_db, check_redis
from backend.engines import (
    broker_costs,
    data_loader,
    earnings,
    factors,
    gonogo,
    macro,
    management,
    markets,
    ollama_ai,
    option_chain,
    portfolio,
    position_sizing,
    research,
    screener,
    sentiment,
    tax_advanced,
    tax_engine,
)
from backend.schemas import (
    CostCalculatorRequest,
    HealthDepsResponse,
    MarketCategory,
    WhenToSellRequest,
)

router = APIRouter(prefix="/api")

# ── Health ────────────────────────────────────────────────────


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/deps", response_model=HealthDepsResponse)
def health_deps() -> HealthDepsResponse:
    return HealthDepsResponse(database=check_db(), redis=check_redis())


# ── Phase 1: Broker Costs ────────────────────────────────────


@router.post("/cost-calculator")
def cost_calculator(body: CostCalculatorRequest) -> dict:
    try:
        return broker_costs.calculate_true_cost(
            broker=broker_costs.Broker(body.broker.value),
            segment=broker_costs.Segment(body.segment.value),
            side=broker_costs.Side(body.side.value),
            quantity=body.quantity,
            price=body.price,
            premium=body.premium,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Phase 1: Basic Tax ───────────────────────────────────────


@router.post("/tax/when-to-sell")
def when_to_sell(body: WhenToSellRequest) -> dict:
    return tax_engine.when_to_sell_analysis(
        purchase_date=body.purchase_date,
        as_of=body.as_of,
        buy_price=body.buy_price,
        last_price=body.last_price,
        quantity=body.quantity,
    )


@router.get("/tax/itm-expiry-warning")
def itm_expiry(intrinsic_per_unit: float, quantity: float) -> dict:
    return tax_engine.itm_option_expiry_stt_warning(intrinsic_per_unit, quantity)


@router.get("/tax/fo-turnover")
def fo_turnover(turnover_ytd_inr: float) -> dict:
    return tax_engine.fo_turnover_alert(turnover_ytd_inr)


# ── Phase 1: Option Chain ────────────────────────────────────


@router.get("/option-chain/{symbol}")
def option_chain_route(symbol: str) -> dict:
    sym = symbol.upper()
    if sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
        payload = nse_fetcher.option_chain_index(sym)
    else:
        payload = nse_fetcher.option_chain_equity(sym)
    return option_chain.analyze_option_chain(payload)


# ── Phase 1: Sentiment ───────────────────────────────────────


@router.get("/sentiment/{ticker:path}")
def sentiment_route(ticker: str) -> dict:
    return sentiment.composite_sentiment(ticker)


@router.get("/market/fii-dii")
def fii_dii() -> dict:
    raw = nse_fetcher.fii_dii_data()
    if raw.get("error"):
        return {"nse": raw, "parsed": None}
    parsed = nse_fetcher.parse_fii_dii_net_crores(raw)
    return {"nse": raw, "parsed": parsed}


# ── Phase 2: GO/NO-GO ────────────────────────────────────────


@router.get("/gonogo/{symbol}")
def gonogo_route(symbol: str) -> dict:
    return gonogo.compute_gonogo(symbol)


# ── Phase 2: Position Sizing ─────────────────────────────────


@router.get("/position-size/{symbol}")
def position_size_route(
    symbol: str,
    capital: float = 1000000,
    risk_pct: float = 0.02,
) -> dict:
    return position_sizing.atr_position_size(symbol, capital, risk_pct)


@router.post("/position-size/kelly")
def kelly_route(body: dict[str, Any]) -> dict:
    return position_sizing.kelly_criterion(
        win_rate=body.get("win_rate", 0.55),
        avg_win=body.get("avg_win", 1000),
        avg_loss=body.get("avg_loss", 800),
        fraction=body.get("fraction", 0.5),
    )


@router.post("/portfolio/concentration")
def concentration_route(body: dict[str, Any]) -> dict:
    return position_sizing.portfolio_concentration_check(
        holdings=body.get("holdings", []),
    )


# ── Phase 2: Macro ───────────────────────────────────────────


@router.get("/macro/regime")
def macro_regime() -> dict:
    return macro.classify_regime()


@router.get("/macro/dashboard")
def macro_dashboard() -> dict:
    return macro.fetch_macro_dashboard()


# ── Phase 2: Screener ────────────────────────────────────────


@router.get("/screener")
def screener_route(top_n: int = 5) -> dict:
    return screener.scan_universe(top_n=top_n)


# ── Phase 2: Earnings ────────────────────────────────────────


@router.get("/earnings/{symbol}")
def earnings_route(symbol: str) -> dict:
    return earnings.earnings_analysis(symbol)


# ── Phase 3: Research ────────────────────────────────────────


@router.post("/research/thesis")
def research_thesis(body: dict[str, Any]) -> dict:
    return research.evaluate_thesis(
        symbol=body.get("symbol", ""),
        thesis=body.get("thesis", ""),
        thesis_type=body.get("thesis_type", "bullish"),
        target_price=body.get("target_price"),
        timeframe_months=body.get("timeframe_months", 12),
    )


# ── Phase 3: Management Quality ──────────────────────────────


@router.get("/management/{symbol}")
def management_route(symbol: str) -> dict:
    return management.management_quality(symbol)


# ── Phase 4: Portfolio Risk ──────────────────────────────────


@router.post("/portfolio/risk")
def portfolio_risk_route(body: dict[str, Any]) -> dict:
    return portfolio.portfolio_risk(
        holdings=body.get("holdings", []),
        period=body.get("period", "1y"),
    )


@router.post("/portfolio/retirement")
def retirement_route(body: dict[str, Any]) -> dict:
    return portfolio.retirement_tracker(
        current_age=body.get("current_age", 30),
        retirement_age=body.get("retirement_age", 60),
        current_corpus=body.get("current_corpus", 0),
        monthly_sip=body.get("monthly_sip", 25000),
        expected_return_pct=body.get("expected_return_pct", 12),
        inflation_pct=body.get("inflation_pct", 6),
        target_monthly_expense=body.get("target_monthly_expense", 100000),
    )


# ── Phase 6: Advanced Tax ────────────────────────────────────


@router.post("/tax/compute")
def tax_compute(body: dict[str, Any]) -> dict:
    gain = body.get("gain", 0)
    treatment_str = body.get("treatment", "india_stcg_equity")
    try:
        treatment = tax_advanced.TaxTreatment(treatment_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid treatment: {treatment_str}")
    result = tax_advanced.compute_india_tax(gain, treatment)
    return {
        "treatment": result.treatment.value,
        "gross_gain": result.gross_gain,
        "tax_amount": result.tax_amount,
        "effective_rate": result.effective_rate,
        "breakdown": result.breakdown,
        "notes": result.notes,
    }


@router.post("/tax/us-india")
def us_tax_route(body: dict[str, Any]) -> dict:
    return tax_advanced.us_tax_india_resident(
        gain_usd=body.get("gain_usd", 0),
        holding_days=body.get("holding_days", 365),
        dividend_usd=body.get("dividend_usd", 0),
        fx_rate=body.get("fx_rate", 83.5),
    )


@router.post("/tax/harvest-scan")
def tax_harvest_route(body: dict[str, Any]) -> list:
    return tax_advanced.tax_loss_harvest_scan(
        positions=body.get("positions", []),
    )


@router.post("/tax/cumulative")
def tax_cumulative_route(body: dict[str, Any]) -> dict:
    return tax_advanced.cumulative_tax_bill(
        transactions=body.get("transactions", []),
    )


# ── Phase 7: Factor Model ────────────────────────────────────


@router.get("/factors/{symbol}")
def factor_route(symbol: str) -> dict:
    return factors.factor_exposure(symbol)


@router.get("/factors/sectors/rotation")
def sector_rotation_route() -> dict:
    return factors.sector_rotation_signals()


@router.get("/factors/credit/{symbol}")
def credit_route(symbol: str) -> dict:
    return factors.credit_score(symbol)


# ── Markets routes — multi-asset global coverage ─────────────


@router.get("/markets/categories")
def market_categories() -> list[dict]:
    return markets.available_categories()


@router.get("/markets/pulse")
def market_pulse() -> dict:
    return markets.global_market_summary()


@router.get("/markets/category/{category}")
def market_category(
    category: str,
    limit: int | None = None,
    offset: int = 0,
    tag: str | None = None,
) -> dict:
    return markets.category_overview(category, limit=limit, offset=offset, tag=tag)


@router.get("/markets/tags")
def market_tags() -> list[dict]:
    """All index-membership / exchange / type tags available for filtering."""
    return markets.available_tags()


@router.post("/markets/universe/refresh")
def market_universe_refresh(fast: bool = False) -> dict:
    """Run the universe downloader (NSE/BSE/AMFI/etc.) in foreground."""
    import threading

    prog = markets.universe_progress()
    if prog.get("running"):
        return {"status": "already_running", "progress": prog}

    def _run():
        markets.refresh_universe(fast=fast)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"status": "started"}


@router.get("/markets/universe/progress")
def market_universe_progress() -> dict:
    return markets.universe_progress()


@router.get("/markets/gainers-losers/{category}")
def market_gainers_losers(category: MarketCategory, top_n: int = 5) -> dict:
    return markets.gainers_losers(category.value, top_n)


@router.get("/markets/quote/{symbol:path}")
def market_quote(symbol: str) -> dict:
    return markets.instrument_detail(symbol)


@router.get("/markets/ticker/{symbol:path}")
def market_ticker_detail(symbol: str) -> dict:
    """Bloomberg-style composite: quote + performance + 1y history + news."""
    return markets.ticker_detail(symbol)


@router.get("/markets/history/{symbol:path}")
def market_history(symbol: str, period: str = "6mo", interval: str = "1d") -> dict:
    return markets.price_history(symbol, period, interval)


@router.get("/markets/news/{symbol:path}")
def market_news(symbol: str) -> dict:
    return markets.symbol_news(symbol)


@router.get("/markets/search")
def market_search(q: str) -> list[dict]:
    return markets.search(q)


@router.get("/markets/metals/india")
def india_metals() -> dict:
    return markets.metal_prices()


# ── Wiki routes ──────────────────────────────────────────────

from backend.data import wiki as wiki_data  # noqa: E402


@router.get("/wiki/categories")
def wiki_categories() -> list[str]:
    return wiki_data.all_categories()


@router.get("/wiki/articles")
def wiki_all_articles() -> list[dict]:
    return [
        {"slug": a["slug"], "title": a["title"], "category": a["category"], "tags": a["tags"]}
        for a in wiki_data.all_articles()
    ]


@router.get("/wiki/category/{category:path}")
def wiki_by_category(category: str) -> list[dict]:
    return wiki_data.articles_by_category(category)


@router.get("/wiki/search")
def wiki_search(q: str) -> list[dict]:
    return [
        {"slug": a["slug"], "title": a["title"], "category": a["category"], "tags": a["tags"]}
        for a in wiki_data.search_articles(q)
    ]


@router.get("/wiki/article/{slug}")
def wiki_article(slug: str) -> dict:
    a = wiki_data.article_by_slug(slug)
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    return a


# ── Data Loader routes ───────────────────────────────────────

import threading  # noqa: E402


@router.post("/data/download")
def start_download() -> dict:
    """Start full data download in background thread."""
    progress = data_loader.get_progress()
    if progress.get("running"):
        return {"status": "already_running", "progress": progress}

    def _run():
        data_loader.run_full_download()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"status": "started"}


@router.get("/data/progress")
def download_progress() -> dict:
    """Poll download progress."""
    return data_loader.get_progress()


@router.get("/data/api-status")
def api_status() -> dict:
    """Check which API keys are configured."""
    s = get_settings()
    return {
        "fred": bool(s.fred_api_key),
        "alpha_vantage": bool(s.alpha_vantage_key),
        "twelve_data": bool(s.twelve_data_key),
        "polygon": bool(s.polygon_key),
        "tiingo": bool(s.tiingo_key),
        "finnhub": bool(s.finnhub_api_key),
        "marketaux": bool(s.marketaux_key),
        "newsapi": bool(s.news_api_key),
        "upstox": bool(s.upstox_access_token),
        "ollama": ollama_ai.is_available().get("available", False),
    }


# ── Ollama AI routes ─────────────────────────────────────────


@router.get("/ai/status")
def ai_status() -> dict:
    return ollama_ai.is_available()


@router.post("/ai/pull")
def ai_pull_model(body: dict[str, Any]) -> dict:
    model = body.get("model", get_settings().ollama_model)
    return ollama_ai.pull_model(model)


@router.post("/ai/chat")
def ai_chat(body: dict[str, Any]) -> dict:
    prompt = body.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    return ollama_ai.chat(prompt)


@router.get("/ai/analyze/{symbol}")
def ai_analyze(symbol: str) -> dict:
    return ollama_ai.analyze_symbol(symbol)


@router.post("/ai/query")
def ai_query(body: dict[str, Any]) -> dict:
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    return ollama_ai.market_query(query)
