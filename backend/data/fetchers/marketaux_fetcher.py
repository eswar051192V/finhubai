"""Marketaux fetcher — news with built-in sentiment scores."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://api.marketaux.com/v1"


def _get(path: str, **params: str) -> dict[str, Any]:
    key = get_settings().marketaux_key
    if not key:
        return {"error": "MARKETAUX_KEY not set"}
    params["api_token"] = key
    r = httpx.get(f"{BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def market_news(
    symbols: str = "", countries: str = "in,us",
    limit: int = 20,
) -> dict[str, Any]:
    params: dict[str, str] = {"limit": str(limit), "countries": countries}
    if symbols:
        params["symbols"] = symbols
    return _get("/news/all", **params)


def sentiment_by_symbol(symbol: str, limit: int = 10) -> dict[str, Any]:
    return _get("/news/all", symbols=symbol, limit=str(limit))
