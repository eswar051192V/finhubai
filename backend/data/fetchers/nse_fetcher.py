from __future__ import annotations

import json
from typing import Any

import httpx

from backend.config import get_settings

NSE_BASE = "https://www.nseindia.com"


def _headers() -> dict[str, str]:
    settings = get_settings()
    h = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-IN,en;q=0.9",
        "Referer": f"{NSE_BASE}/option-chain",
    }
    if settings.nse_cookies:
        h["Cookie"] = settings.nse_cookies
    return h


def _get_json(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    url = f"{NSE_BASE}{path}"
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        r = client.get(url, headers=_headers(), params=params)
        if r.status_code in (401, 403):
            return {
                "error": "nse_auth",
                "status_code": r.status_code,
                "hint": "Set NSE_COOKIES in .env from a logged-in browser session, or retry later.",
            }
        r.raise_for_status()
        return r.json()


def option_chain_equity(symbol: str) -> dict[str, Any]:
    sym = symbol.upper().replace(".NS", "").replace(".BO", "")
    try:
        data = _get_json("/api/option-chain-equities", params={"symbol": sym})
    except httpx.HTTPError as e:
        return {"error": "nse_http", "detail": str(e)}
    if "error" in data:
        return data
    return {"symbol": sym, "records": data}


def option_chain_index(symbol: str) -> dict[str, Any]:
    sym = symbol.upper()
    try:
        data = _get_json("/api/option-chain-indices", params={"symbol": sym})
    except httpx.HTTPError as e:
        return {"error": "nse_http", "detail": str(e)}
    if "error" in data:
        return data
    return {"symbol": sym, "records": data}


def fii_dii_data() -> dict[str, Any]:
    """Latest FII/DII cash market figures when NSE JSON is available."""
    try:
        data = _get_json("/api/fiidiidata")
    except httpx.HTTPError as e:
        return {"error": "nse_http", "detail": str(e)}
    if "error" in data:
        return data
    return {"raw": data}


def parse_fii_dii_net_crores(payload: dict[str, Any]) -> dict[str, Any]:
    """Best-effort parse of NSE fiidiidata shape (keys vary)."""
    if "raw" not in payload:
        return {"fii_net_crores": None, "dii_net_crores": None, "note": "no raw payload"}
    raw = payload["raw"]
    text_blob = json.dumps(raw)
    # Fallback: user sees raw in API response
    fii = dii = None
    if isinstance(raw, dict):
        # common pattern: list under 'data' with category/net values
        rows = raw.get("data") or raw.get("fiiDiiData") or []
        if isinstance(rows, list) and rows:
            for row in rows:
                if not isinstance(row, dict):
                    continue
                cat = str(row.get("category", "")).lower()
                net = row.get("fiiNet") or row.get("fii_net") or row.get("net")
                if net is None:
                    continue
                try:
                    val = float(net)
                except (TypeError, ValueError):
                    continue
                if "foreign" in cat or "fii" in cat:
                    fii = val
                if "domestic" in cat or "dii" in cat:
                    dii = val
    return {
        "fii_net_crores": fii,
        "dii_net_crores": dii,
        "parse_note": "Heuristic parse; verify against NSE PDF/table.",
        "raw_keys": list(raw.keys()) if isinstance(raw, dict) else None,
        "sample": text_blob[:500],
    }
