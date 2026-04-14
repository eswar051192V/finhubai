"""Upstox API fetcher — live quotes, historical candles, holdings."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://api.upstox.com/v2"


def _headers() -> dict[str, str]:
    token = get_settings().upstox_access_token
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _get(path: str, **params: str) -> dict[str, Any]:
    token = get_settings().upstox_access_token
    if not token:
        return {"error": "UPSTOX_ACCESS_TOKEN not set"}
    r = httpx.get(f"{BASE}{path}", headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def market_quote(instrument_key: str) -> dict[str, Any]:
    return _get("/market-quote/quotes", instrument_key=instrument_key)


def historical_candle(
    instrument_key: str, interval: str = "day",
    from_date: str = "", to_date: str = "",
) -> dict[str, Any]:
    path = f"/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"
    return _get(path)


def holdings() -> dict[str, Any]:
    return _get("/portfolio/long-term-holdings")


def positions() -> dict[str, Any]:
    return _get("/portfolio/short-term-positions")


def funds_and_margin() -> dict[str, Any]:
    return _get("/user/get-funds-and-margin")
