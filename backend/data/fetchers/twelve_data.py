"""Twelve Data fetcher — real-time + historical prices, technicals."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://api.twelvedata.com"


def _get(path: str, **params: str) -> dict[str, Any]:
    key = get_settings().twelve_data_key
    if not key:
        return {"error": "TWELVE_DATA_KEY not set"}
    params["apikey"] = key
    r = httpx.get(f"{BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def time_series(
    symbol: str, interval: str = "1day", outputsize: int = 30,
) -> dict[str, Any]:
    return _get(
        "/time_series",
        symbol=symbol,
        interval=interval,
        outputsize=str(outputsize),
    )


def quote(symbol: str) -> dict[str, Any]:
    return _get("/quote", symbol=symbol)


def technical_indicator(
    symbol: str, indicator: str = "rsi",
    interval: str = "1day", time_period: int = 14,
) -> dict[str, Any]:
    return _get(
        f"/{indicator}",
        symbol=symbol,
        interval=interval,
        time_period=str(time_period),
    )


def stocks_list() -> dict[str, Any]:
    return _get("/stocks")


def forex_pairs() -> dict[str, Any]:
    return _get("/forex_pairs")


def crypto_list() -> dict[str, Any]:
    return _get("/cryptocurrencies")
