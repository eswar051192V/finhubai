"""NewsAPI fetcher — global news headlines with keyword search."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)
BASE = "https://newsapi.org/v2"


def _get(path: str, **params: str) -> dict[str, Any]:
    key = get_settings().news_api_key
    if not key:
        return {"error": "NEWS_API_KEY not set"}
    params["apiKey"] = key
    r = httpx.get(f"{BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def top_headlines(
    country: str = "us", category: str = "business", page_size: int = 20,
) -> dict[str, Any]:
    return _get(
        "/top-headlines",
        country=country, category=category, pageSize=str(page_size),
    )


def search_news(query: str, sort_by: str = "publishedAt", page_size: int = 20) -> dict[str, Any]:
    return _get("/everything", q=query, sortBy=sort_by, pageSize=str(page_size))
