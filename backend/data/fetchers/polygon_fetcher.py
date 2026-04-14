"""Polygon.io fetcher — historical bars, tickers, and reference data."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://api.polygon.io"


def _get(path: str, **params: str) -> dict[str, Any]:
    key = get_settings().polygon_key
    if not key:
        return {"error": "POLYGON_KEY not set"}
    params["apiKey"] = key
    r = httpx.get(f"{BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def ticker_details(ticker: str) -> dict[str, Any]:
    return _get(f"/v3/reference/tickers/{ticker}")


def agg_bars(
    ticker: str, from_date: str, to_date: str,
    timespan: str = "day", multiplier: int = 1,
) -> dict[str, Any]:
    return _get(
        f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}",
        limit="50000",
    )


def grouped_daily(date: str) -> dict[str, Any]:
    return _get(f"/v2/aggs/grouped/locale/us/market/stocks/{date}")


def previous_close(ticker: str) -> dict[str, Any]:
    return _get(f"/v2/aggs/ticker/{ticker}/prev")


def tickers_list(market: str = "stocks", limit: int = 1000) -> dict[str, Any]:
    return _get("/v3/reference/tickers", market=market, limit=str(limit), active="true")


def ticker_news(ticker: str, limit: int = 20) -> dict[str, Any]:
    return _get("/v2/reference/news", ticker=ticker, limit=str(limit))
