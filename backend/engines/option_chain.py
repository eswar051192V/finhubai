"""Option chain analytics from NSE JSON."""

from __future__ import annotations

from statistics import mean
from typing import Any


def _chain_rows_and_underlying(nse_payload: dict[str, Any]) -> tuple[list[dict[str, Any]], float | None]:
    """Normalize NSE option-chain JSON (nested `records`) into strike rows."""
    top = nse_payload.get("records") or {}
    if not isinstance(top, dict):
        return [], None
    inner = top.get("records", top)
    if not isinstance(inner, dict):
        return [], None
    rows = list(inner.get("data") or [])
    u = inner.get("underlyingValue")
    try:
        underlying = float(u) if u is not None else None
    except (TypeError, ValueError):
        underlying = None
    return rows, underlying


def max_pain(rows: list[dict[str, Any]], underlying: float | None) -> dict[str, Any]:
    """
    Classic max pain: strike minimizing total payout assuming OI is writer exposure.
    Uses intrinsic * OI per strike; lot size ignored (relative ranking usually stable).
    """
    strikes: list[float] = []
    for row in rows:
        sp = row.get("strikePrice")
        if sp is not None:
            try:
                strikes.append(float(sp))
            except (TypeError, ValueError):
                continue
    strikes = sorted(set(strikes))
    if not strikes:
        return {"max_pain": None, "note": "no strikes"}

    def oi_for(strike: float, opt: str) -> float:
        total = 0.0
        for row in rows:
            try:
                if float(row.get("strikePrice", -1)) != strike:
                    continue
            except (TypeError, ValueError):
                continue
            side = row.get(opt) or {}
            oi = side.get("openInterest") or side.get("openInterestInLot") or 0
            try:
                total += float(oi)
            except (TypeError, ValueError):
                continue
        return total

    best_strike = None
    best_pain = float("inf")
    for k in strikes:
        pain = 0.0
        for s in strikes:
            ce_oi = oi_for(s, "CE")
            pe_oi = oi_for(s, "PE")
            pain += ce_oi * max(0.0, s - k)
            pain += pe_oi * max(0.0, k - s)
        if pain < best_pain:
            best_pain = pain
            best_strike = k

    return {
        "max_pain": best_strike,
        "total_pain_score": round(best_pain, 2) if best_strike is not None else None,
        "underlying": underlying,
    }


def pcr(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pe_oi = ce_oi = 0.0
    for row in rows:
        ce = row.get("CE") or {}
        pe = row.get("PE") or {}
        for side, key in ((ce, "ce"), (pe, "pe")):
            oi = side.get("openInterest") or 0
            try:
                oi = float(oi)
            except (TypeError, ValueError):
                oi = 0.0
            if key == "ce":
                ce_oi += oi
            else:
                pe_oi += oi
    ratio = (pe_oi / ce_oi) if ce_oi else None
    interp = None
    if ratio is not None:
        if ratio > 1.2:
            interp = "elevated_put_oi_vs_call"
        elif ratio < 0.8:
            interp = "elevated_call_oi_vs_put"
        else:
            interp = "balanced"
    return {"put_oi": pe_oi, "call_oi": ce_oi, "pcr_oi": ratio, "interpretation": interp}


def oi_change_heuristic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify aggregate OI change hints when `changeinOpenInterest` exists."""
    ce_long = ce_short = pe_long = pe_short = 0.0
    for row in rows:
        for opt_key in ("CE", "PE"):
            side = row.get(opt_key) or {}
            ch = side.get("changeinOpenInterest") or side.get("pchangeinOpenInterest")
            try:
                ch = float(ch)
            except (TypeError, ValueError):
                continue
            if opt_key == "CE":
                if ch > 0:
                    ce_long += ch
                else:
                    ce_short += abs(ch)
            elif ch > 0:
                pe_long += ch
            else:
                pe_short += abs(ch)
    return {
        "ce_oi_increase": ce_long,
        "ce_oi_decrease": ce_short,
        "pe_oi_increase": pe_long,
        "pe_oi_decrease": pe_short,
        "note": "Heuristic only; inspect strike-level OI for positioning stories.",
    }


def iv_percentile_current(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ivs: list[float] = []
    for row in rows:
        for opt in ("CE", "PE"):
            side = row.get(opt) or {}
            iv = side.get("impliedVolatility") or side.get("impliedVolatilityInPercentage")
            if iv is None:
                continue
            try:
                ivs.append(float(iv))
            except (TypeError, ValueError):
                continue
    if not ivs:
        return {"iv_percentile": None, "note": "No IV in chain; index options often omit per-row IV."}
    # Without history, report distribution vs current chain as a weak proxy
    avg_iv = mean(ivs)
    return {
        "iv_mean_chain": round(avg_iv, 4),
        "iv_min": round(min(ivs), 4),
        "iv_max": round(max(ivs), 4),
        "note": "True IV percentile needs historical IV time series.",
    }


def analyze_option_chain(nse_payload: dict[str, Any]) -> dict[str, Any]:
    if "error" in nse_payload:
        return nse_payload
    rows, u = _chain_rows_and_underlying(nse_payload)
    return {
        "symbol": nse_payload.get("symbol"),
        "underlying": u,
        "max_pain": max_pain(rows, u),
        "pcr": pcr(rows),
        "oi_change": oi_change_heuristic(rows),
        "iv": iv_percentile_current(rows),
    }
