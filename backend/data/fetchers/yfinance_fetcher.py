from __future__ import annotations

from typing import Any

import yfinance as yf


def quote_summary(ticker: str) -> dict[str, Any]:
    t = yf.Ticker(ticker)
    fi = t.fast_info
    last = None
    if isinstance(fi, dict):
        last = fi.get("last_price") or fi.get("lastPrice")
    else:
        last = getattr(fi, "last_price", None) or getattr(fi, "lastPrice", None)
    if last is None:
        hist = t.history(period="5d")
        if hist is not None and not hist.empty:
            last = float(hist["Close"].iloc[-1])
    currency = fi.get("currency") if isinstance(fi, dict) else getattr(fi, "currency", None)
    return {
        "ticker": ticker,
        "last_price": float(last) if last is not None else None,
        "currency": currency,
    }
