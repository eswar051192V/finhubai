# ruff: noqa: E501
"""
Morning Scanner / Screener — scans a universe of stocks for top
opportunities based on momentum, volume, and value signals.
"""
from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

log = logging.getLogger(__name__)

NIFTY_50_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "TATAMOTORS.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ONGC.NS", "NTPC.NS", "ADANIENT.NS",
    "WIPRO.NS", "POWERGRID.NS", "TATASTEEL.NS", "ASIANPAINT.NS", "JSWSTEEL.NS",
]


def scan_universe(
    symbols: list[str] | None = None,
    top_n: int = 5,
) -> dict[str, Any]:
    """
    Scan a list of symbols and rank by composite momentum/value score.
    Returns top gainers, top losers, and unusual volume.
    """
    universe = symbols or NIFTY_50_SYMBOLS
    results: list[dict[str, Any]] = []

    for sym in universe:
        try:
            t = yf.Ticker(sym)
            fi = t.fast_info
            last = getattr(fi, "last_price", None) or getattr(fi, "lastPrice", None)
            prev = getattr(fi, "previous_close", None) or getattr(fi, "previousClose", None)

            if last is None:
                hist = t.history(period="5d")
                if hist is not None and not hist.empty:
                    last = float(hist["Close"].iloc[-1])
                    if len(hist) > 1:
                        prev = float(hist["Close"].iloc[-2])

            change_pct = None
            if last and prev:
                try:
                    change_pct = round(((last / prev) - 1) * 100, 2)
                except (TypeError, ZeroDivisionError):
                    pass

            info = {}
            try:
                info = t.info or {}
            except Exception:
                pass

            avg_vol = info.get("averageVolume")
            cur_vol = info.get("volume")
            vol_ratio = None
            if avg_vol and cur_vol and avg_vol > 0:
                vol_ratio = round(cur_vol / avg_vol, 2)

            results.append({
                "symbol": sym,
                "name": info.get("shortName", sym.replace(".NS", "")),
                "last": round(float(last), 2) if last else None,
                "change_pct": change_pct,
                "volume_ratio": vol_ratio,
                "pe": info.get("trailingPE"),
                "market_cap": info.get("marketCap"),
            })
        except Exception as e:
            log.warning("Screener skip %s: %s", sym, e)

    with_change = [r for r in results if r.get("change_pct") is not None]
    sorted_by_change = sorted(with_change, key=lambda x: x["change_pct"], reverse=True)

    unusual_volume = sorted(
        [r for r in results if r.get("volume_ratio") and r["volume_ratio"] > 1.5],
        key=lambda x: x["volume_ratio"],
        reverse=True,
    )

    return {
        "scanned": len(results),
        "top_gainers": sorted_by_change[:top_n],
        "top_losers": sorted_by_change[-top_n:][::-1] if len(sorted_by_change) >= top_n else [],
        "unusual_volume": unusual_volume[:top_n],
        "all": results,
    }
