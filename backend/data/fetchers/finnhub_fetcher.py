from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings


def company_news(symbol: str, days: int = 7) -> dict[str, Any]:
    settings = get_settings()
    if not settings.finnhub_api_key:
        return {"symbol": symbol, "items": [], "error": "missing_finnhub_api_key"}
    url = "https://finnhub.io/api/v1/company-news"
    params = {"symbol": symbol.upper(), "token": settings.finnhub_api_key}
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params)
        if r.status_code == 403:
            return {"symbol": symbol, "items": [], "error": "finnhub_forbidden"}
        r.raise_for_status()
        data = r.json()
    if not isinstance(data, list):
        return {"symbol": symbol, "items": [], "raw": data}
    return {"symbol": symbol, "items": data[:50]}
