"""
Markets engine — orchestrates multi-asset data, global overview,
and cross-category analytics.
"""

from __future__ import annotations

from typing import Any

from backend.data.fetchers import markets_fetcher


def global_market_summary() -> dict[str, Any]:
    """
    Quick pulse: one representative from each major category.
    Used by the dashboard to show a single-glance overview.
    """
    pulse_symbols = {
        "nifty50": "^NSEI",
        "sensex": "^BSESN",
        "sp500": "^GSPC",
        "nasdaq": "^IXIC",
        "dow": "^DJI",
        "gold": "GC=F",
        "silver": "SI=F",
        "wti_crude": "CL=F",
        "brent_crude": "BZ=F",
        "natural_gas": "NG=F",
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "usdinr": "USDINR=X",
        "eurusd": "EURUSD=X",
        "us_10y": "^TNX",
        "vix": "^VIX",
        "dxy": "DX-Y.NYB",
    }
    quotes = markets_fetcher._yf_batch_quotes(list(pulse_symbols.values()))
    items: list[dict[str, Any]] = []
    for key, sym in pulse_symbols.items():
        q = quotes.get(sym, {})
        items.append({
            "id": key,
            "symbol": sym,
            "last": q.get("last"),
            "change_pct": q.get("change_pct"),
            "currency": q.get("currency"),
        })
    return {"pulse": items}


def category_overview(
    category: str,
    limit: int | None = None,
    offset: int = 0,
    tag: str | None = None,
) -> dict[str, Any]:
    """Full quote table for a category. Supports pagination + tag filter."""
    return markets_fetcher.fetch_category(
        category, limit=limit, offset=offset, tag=tag
    )


def refresh_universe(fast: bool = False) -> dict[str, Any]:
    """Run the big universe download and reload the registry."""
    from backend.data import universe_loader

    counts = universe_loader.refresh_all(fast=fast)
    loaded = markets_fetcher.reload_extended_registry()
    return {"downloaded": counts, "loaded": loaded}


def universe_progress() -> dict[str, Any]:
    from backend.data import universe_loader

    return universe_loader.get_progress()


def available_tags() -> list[dict[str, Any]]:
    return markets_fetcher.list_available_tags()


def instrument_detail(symbol: str) -> dict[str, Any]:
    """Detailed info for a single instrument."""
    return markets_fetcher.fetch_single_quote(symbol)


def search(query: str) -> list[dict[str, Any]]:
    """Cross-category search."""
    return markets_fetcher.search_symbol(query)


def price_history(
    symbol: str, period: str = "6mo", interval: str = "1d",
) -> dict[str, Any]:
    """Historical OHLCV for charting."""
    return markets_fetcher.fetch_price_history(symbol, period, interval)


def symbol_news(symbol: str) -> dict[str, Any]:
    """News articles for a specific symbol."""
    return markets_fetcher.fetch_symbol_news(symbol)


def metal_prices() -> dict[str, Any]:
    """Gold and silver by Indian city."""
    return markets_fetcher.india_metal_prices_by_city()


def available_categories() -> list[dict[str, Any]]:
    """List all supported categories."""
    return markets_fetcher.list_categories()


def ticker_detail(symbol: str) -> dict[str, Any]:
    """
    Composite Bloomberg-style detail payload for a single symbol.
    Aggregates quote, performance over multiple periods, recent price
    history (for chart), and news in one round-trip.
    """
    quote = markets_fetcher.fetch_single_quote(symbol)

    performance: dict[str, Any] = {}
    try:
        hist = markets_fetcher.fetch_price_history(symbol, "5y", "1d")
        points = hist.get("points") or []
        if points:
            closes = [p["close"] for p in points if p.get("close") is not None]
            dates = [p["date"] for p in points]
            last_close = closes[-1] if closes else None

            def pct_from(idx: int) -> float | None:
                if last_close is None or idx < 0 or idx >= len(closes):
                    return None
                base = closes[idx]
                if not base:
                    return None
                return (last_close - base) / base * 100.0

            # approximate trading-day windows
            n = len(closes)
            performance = {
                "1d": pct_from(n - 2) if n >= 2 else None,
                "5d": pct_from(n - 6) if n >= 6 else None,
                "1m": pct_from(n - 22) if n >= 22 else None,
                "3m": pct_from(n - 66) if n >= 66 else None,
                "6m": pct_from(n - 132) if n >= 132 else None,
                "ytd": None,
                "1y": pct_from(n - 252) if n >= 252 else None,
                "5y": pct_from(0) if n >= 1 else None,
            }
            # YTD: find first trading day of current year
            if dates:
                import datetime as _dt
                try:
                    year = _dt.date.today().year
                    for i, d in enumerate(dates):
                        if d.startswith(str(year)):
                            performance["ytd"] = pct_from(i)
                            break
                except Exception:
                    pass
    except Exception as e:
        performance = {"error": str(e)}

    news = {}
    try:
        news = markets_fetcher.fetch_symbol_news(symbol)
    except Exception as e:
        news = {"symbol": symbol, "articles": [], "error": str(e)}

    history_1y = {}
    try:
        history_1y = markets_fetcher.fetch_price_history(symbol, "1y", "1d")
    except Exception as e:
        history_1y = {"symbol": symbol, "points": [], "error": str(e)}

    return {
        "quote": quote,
        "performance": performance,
        "history": history_1y,
        "news": news,
    }


def gainers_losers(category: str, top_n: int = 5) -> dict[str, Any]:
    """Top gainers and losers in a category by change_pct."""
    data = markets_fetcher.fetch_category(category)
    if "error" in data:
        return data
    instruments = data.get("instruments", [])
    with_change = [
        i for i in instruments
        if i.get("change_pct") is not None
    ]
    sorted_up = sorted(
        with_change, key=lambda x: x["change_pct"], reverse=True
    )
    return {
        "category": category,
        "gainers": sorted_up[:top_n],
        "losers": sorted_up[-top_n:][::-1] if len(sorted_up) >= top_n else sorted_up[::-1],
    }
