from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings


def latest_observation(series_id: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.fred_api_key:
        return {
            "series_id": series_id,
            "error": "missing_fred_api_key",
            "value": None,
        }
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    obs = data.get("observations") or []
    if not obs:
        return {"series_id": series_id, "value": None, "raw": data}
    row = obs[0]
    val = row.get("value")
    return {
        "series_id": series_id,
        "date": row.get("date"),
        "value": float(val) if val not in (None, ".") else None,
    }
