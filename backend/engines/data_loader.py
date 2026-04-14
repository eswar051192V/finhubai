# ruff: noqa: E501
"""
Comprehensive Data Loader — downloads ALL company data, prices,
fundamentals, news, and macro indicators from every configured source.
Tracks progress per-task for the UI.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any

import yfinance as yf

from backend.config import get_settings
from backend.data.fetchers import markets_fetcher

log = logging.getLogger(__name__)

# Global progress tracker (in-process; for production use Redis)
_progress: dict[str, Any] = {
    "running": False,
    "started_at": None,
    "tasks": {},
    "completed": 0,
    "total": 0,
    "errors": [],
}


def get_progress() -> dict[str, Any]:
    return dict(_progress)


def _update(task: str, status: str, detail: str = ""):
    _progress["tasks"][task] = {
        "status": status,
        "detail": detail,
        "timestamp": datetime.now().isoformat(),
    }
    if status == "done":
        _progress["completed"] = _progress.get("completed", 0) + 1
    log.info("[loader] %s: %s %s", task, status, detail)


# ── Universe definitions ──────────────────────────────────────

INDIA_NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "TATAMOTORS.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ONGC.NS", "NTPC.NS", "ADANIENT.NS",
    "WIPRO.NS", "POWERGRID.NS", "TATASTEEL.NS", "ASIANPAINT.NS", "JSWSTEEL.NS",
    "HCLTECH.NS", "BAJAJFINSV.NS", "NESTLEIND.NS", "ULTRACEMCO.NS", "TECHM.NS",
    "M&M.NS", "HINDALCO.NS", "INDUSINDBK.NS", "CIPLA.NS", "DRREDDY.NS",
    "SBILIFE.NS", "GRASIM.NS", "DIVISLAB.NS", "BRITANNIA.NS", "EICHERMOT.NS",
    "APOLLOHOSP.NS", "COALINDIA.NS", "BPCL.NS", "TATACONSUM.NS", "HEROMOTOCO.NS",
    "ADANIPORTS.NS", "BAJAJ-AUTO.NS", "SHRIRAMFIN.NS", "LTIM.NS", "VEDL.NS",
]

US_SP500_TOP50 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "JNJ", "UNH", "XOM", "PG", "MA", "HD", "CVX", "ABBV",
    "MRK", "PEP", "KO", "COST", "AVGO", "TMO", "WMT", "DIS", "NFLX",
    "AMD", "INTC", "BA", "LLY", "ORCL", "CRM", "ADBE", "CSCO", "ACN",
    "TXN", "QCOM", "AMAT", "GS", "MS", "BLK", "SCHW", "AXP", "CAT",
    "GE", "DE", "RTX", "HON", "NEE",
]

CRYPTO_TOP = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD",
    "DOGE-USD", "DOT-USD", "AVAX-USD", "MATIC-USD", "LINK-USD",
]

COMMODITIES_FOREX = [
    "GC=F", "SI=F", "CL=F", "BZ=F", "NG=F", "HG=F", "PL=F",
    "ZW=F", "ZC=F", "ZS=F", "KC=F",
    "USDINR=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X",
    "^GSPC", "^DJI", "^IXIC", "^NSEI", "^BSESN",
]

FRED_SERIES = {
    "GDP Growth": "A191RL1Q225SBEA",
    "CPI All Urban": "CPIAUCSL",
    "Unemployment": "UNRATE",
    "Fed Funds Rate": "FEDFUNDS",
    "10Y Treasury": "DGS10",
    "2Y Treasury": "DGS2",
    "10Y-2Y Spread": "T10Y2Y",
    "VIX": "VIXCLS",
    "M2 Money Supply": "M2SL",
    "Industrial Production": "INDPRO",
    "Consumer Confidence": "UMCSENT",
    "Personal Savings Rate": "PSAVERT",
    "Initial Claims": "ICSA",
    "Real GDP": "GDPC1",
    "Core PCE": "PCEPILFE",
}


def _download_yf_history(symbols: list[str], period: str, task_name: str) -> dict[str, Any]:
    """Download historical data for a batch of symbols via yfinance."""
    _update(task_name, "running", f"0/{len(symbols)} symbols")
    results: dict[str, Any] = {}
    for i, sym in enumerate(symbols):
        try:
            t = yf.Ticker(sym)
            hist = t.history(period=period)
            info = {}
            try:
                info = t.info or {}
            except Exception:
                pass
            rows = len(hist) if hist is not None else 0
            results[sym] = {
                "rows": rows,
                "name": info.get("shortName", sym),
                "sector": info.get("sector"),
                "market_cap": info.get("marketCap"),
                "pe": info.get("trailingPE"),
                "last": float(hist["Close"].iloc[-1]) if rows > 0 else None,
            }
        except Exception as e:
            results[sym] = {"error": str(e)}
            _progress["errors"].append(f"{sym}: {e}")
        _update(task_name, "running", f"{i + 1}/{len(symbols)} symbols")
        time.sleep(0.3)
    _update(task_name, "done", f"{len(results)} symbols downloaded")
    return results


def _download_fred(task_name: str) -> dict[str, Any]:
    """Download FRED macro indicators."""
    from backend.data.fetchers import fred_fetcher
    _update(task_name, "running", f"0/{len(FRED_SERIES)} indicators")
    results: dict[str, Any] = {}
    for i, (name, series_id) in enumerate(FRED_SERIES.items()):
        try:
            obs = fred_fetcher.latest_observation(series_id)
            results[name] = obs
        except Exception as e:
            results[name] = {"error": str(e)}
        _update(task_name, "running", f"{i + 1}/{len(FRED_SERIES)} indicators")
        time.sleep(0.2)
    _update(task_name, "done", f"{len(results)} FRED indicators")
    return results


def _download_news(task_name: str) -> dict[str, Any]:
    """Download latest market news from all configured sources."""
    _update(task_name, "running", "Fetching from Finnhub, Marketaux, NewsAPI...")
    results: dict[str, Any] = {}
    settings = get_settings()

    if settings.finnhub_api_key:
        try:
            from backend.data.fetchers import finnhub_fetcher
            news = finnhub_fetcher.company_news("AAPL")
            results["finnhub"] = {"count": len(news) if isinstance(news, list) else 0}
        except Exception as e:
            results["finnhub"] = {"error": str(e)}

    if settings.marketaux_key:
        try:
            from backend.data.fetchers import marketaux_fetcher
            news = marketaux_fetcher.market_news()
            results["marketaux"] = {"count": len(news.get("data", []))}
        except Exception as e:
            results["marketaux"] = {"error": str(e)}

    if settings.news_api_key:
        try:
            from backend.data.fetchers import newsapi_fetcher
            news = newsapi_fetcher.top_headlines()
            results["newsapi"] = {"count": news.get("totalResults", 0)}
        except Exception as e:
            results["newsapi"] = {"error": str(e)}

    _update(task_name, "done", f"{len(results)} news sources")
    return results


def _download_polygon(task_name: str) -> dict[str, Any]:
    """Fetch reference data from Polygon."""
    settings = get_settings()
    if not settings.polygon_key:
        _update(task_name, "done", "Polygon key not set — skipped")
        return {"skipped": True}
    _update(task_name, "running", "Fetching ticker list...")
    try:
        from backend.data.fetchers import polygon_fetcher
        tickers = polygon_fetcher.tickers_list(limit=100)
        count = len(tickers.get("results", []))
        _update(task_name, "done", f"{count} tickers from Polygon")
        return {"count": count}
    except Exception as e:
        _update(task_name, "done", f"Polygon error: {e}")
        return {"error": str(e)}


def _download_twelve_data(task_name: str) -> dict[str, Any]:
    """Fetch available instruments from Twelve Data."""
    settings = get_settings()
    if not settings.twelve_data_key:
        _update(task_name, "done", "Twelve Data key not set — skipped")
        return {"skipped": True}
    _update(task_name, "running", "Fetching instrument lists...")
    try:
        from backend.data.fetchers import twelve_data
        stocks = twelve_data.stocks_list()
        count = len(stocks.get("data", []))
        _update(task_name, "done", f"{count} stocks from Twelve Data")
        return {"count": count}
    except Exception as e:
        _update(task_name, "done", f"Twelve Data error: {e}")
        return {"error": str(e)}


def _download_alpha_vantage_fundamentals(task_name: str) -> dict[str, Any]:
    """Fetch company fundamentals from Alpha Vantage for key stocks."""
    settings = get_settings()
    if not settings.alpha_vantage_key:
        _update(task_name, "done", "Alpha Vantage key not set — skipped")
        return {"skipped": True}
    _update(task_name, "running", "Fetching fundamentals (rate-limited)...")
    from backend.data.fetchers import alpha_vantage
    top_symbols = ["AAPL", "MSFT", "GOOGL", "RELIANCE.BSE", "TCS.BSE"]
    results: dict[str, Any] = {}
    for i, sym in enumerate(top_symbols):
        try:
            overview = alpha_vantage.company_overview(sym)
            results[sym] = {
                "name": overview.get("Name"),
                "sector": overview.get("Sector"),
                "pe": overview.get("PERatio"),
                "market_cap": overview.get("MarketCapitalization"),
            }
        except Exception as e:
            results[sym] = {"error": str(e)}
        _update(task_name, "running", f"{i + 1}/{len(top_symbols)} (12s rate limit)")
        time.sleep(12)
    _update(task_name, "done", f"{len(results)} fundamentals downloaded")
    return results


def run_full_download() -> dict[str, Any]:
    """
    Master download — runs all data pulls sequentially.
    Returns summary of everything downloaded.
    """
    global _progress
    _progress = {
        "running": True,
        "started_at": datetime.now().isoformat(),
        "tasks": {},
        "completed": 0,
        "total": 9,
        "errors": [],
    }
    results: dict[str, Any] = {}

    try:
        results["india_equity"] = _download_yf_history(
            INDIA_NIFTY_50, "1y", "India NIFTY 50 (1Y history)"
        )
        results["us_equity"] = _download_yf_history(
            US_SP500_TOP50, "1y", "US S&P 500 Top 50 (1Y history)"
        )
        results["crypto"] = _download_yf_history(
            CRYPTO_TOP, "1y", "Crypto Top 11 (1Y history)"
        )
        results["commodities_forex"] = _download_yf_history(
            COMMODITIES_FOREX, "1y", "Commodities, Forex & Indices (1Y)"
        )
        results["fred_macro"] = _download_fred("FRED Macro Indicators")
        results["news"] = _download_news("Market News (all sources)")
        results["polygon"] = _download_polygon("Polygon Reference Data")
        results["twelve_data"] = _download_twelve_data("Twelve Data Instruments")
        results["alpha_vantage"] = _download_alpha_vantage_fundamentals(
            "Alpha Vantage Fundamentals"
        )
    except Exception as e:
        _progress["errors"].append(f"Fatal: {e}")
        log.exception("Data loader failed")

    _progress["running"] = False
    _progress["finished_at"] = datetime.now().isoformat()

    total_symbols = (
        len(results.get("india_equity", {}))
        + len(results.get("us_equity", {}))
        + len(results.get("crypto", {}))
        + len(results.get("commodities_forex", {}))
    )

    return {
        "total_symbols": total_symbols,
        "fred_indicators": len(results.get("fred_macro", {})),
        "errors": _progress["errors"],
        "tasks": _progress["tasks"],
    }
