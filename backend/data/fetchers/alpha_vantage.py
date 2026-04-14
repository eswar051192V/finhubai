"""Alpha Vantage fetcher — fundamentals, earnings, and daily prices."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://www.alphavantage.co/query"


def _get(function: str, **params: str) -> dict[str, Any]:
    key = get_settings().alpha_vantage_key
    if not key:
        return {"error": "ALPHA_VANTAGE_KEY not set"}
    params["function"] = function
    params["apikey"] = key
    r = httpx.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def company_overview(symbol: str) -> dict[str, Any]:
    return _get("OVERVIEW", symbol=symbol)


def income_statement(symbol: str) -> dict[str, Any]:
    return _get("INCOME_STATEMENT", symbol=symbol)


def balance_sheet(symbol: str) -> dict[str, Any]:
    return _get("BALANCE_SHEET", symbol=symbol)


def cash_flow(symbol: str) -> dict[str, Any]:
    return _get("CASH_FLOW", symbol=symbol)


def earnings(symbol: str) -> dict[str, Any]:
    return _get("EARNINGS", symbol=symbol)


def daily_prices(symbol: str, outputsize: str = "compact") -> dict[str, Any]:
    return _get("TIME_SERIES_DAILY", symbol=symbol, outputsize=outputsize)
