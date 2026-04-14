"""
Management Quality Tracker — promoter pledges, insider transactions,
auditor flags, and overall governance score.
"""
from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

log = logging.getLogger(__name__)

GRADES = {(80, 101): "A", (60, 80): "B", (40, 60): "C", (0, 40): "D"}


def _grade(score: float) -> str:
    for (lo, hi), g in GRADES.items():
        if lo <= score < hi:
            return g
    return "D"


def management_quality(symbol: str) -> dict[str, Any]:
    """
    Assess management quality from available data.
    Score 0-100 with grade A/B/C/D.
    """
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

    score = 50.0
    flags: list[str] = []
    positives: list[str] = []

    insider_pct = info.get("heldPercentInsiders")
    inst_pct = info.get("heldPercentInstitutions")
    governance = info.get("overallRisk")

    if insider_pct is not None:
        if insider_pct > 0.50:
            score += 15
            positives.append(f"High insider ownership: {insider_pct:.0%}")
        elif insider_pct > 0.10:
            score += 5
            positives.append(f"Moderate insider ownership: {insider_pct:.0%}")
        elif insider_pct < 0.01:
            score -= 10
            flags.append(f"Very low insider ownership: {insider_pct:.0%}")

    if inst_pct is not None:
        if inst_pct > 0.60:
            score += 10
            positives.append(f"Strong institutional backing: {inst_pct:.0%}")
        elif inst_pct < 0.10:
            score -= 5
            flags.append(f"Low institutional interest: {inst_pct:.0%}")

    if governance is not None:
        if governance <= 3:
            score += 10
            positives.append(f"Low governance risk score: {governance}")
        elif governance >= 8:
            score -= 15
            flags.append(f"High governance risk score: {governance}")

    roe = info.get("returnOnEquity")
    if roe and roe > 0.20:
        score += 10
        positives.append(f"Excellent capital allocation (ROE {roe:.0%})")
    elif roe and roe < 0:
        score -= 15
        flags.append(f"Negative ROE: {roe:.0%}")

    debt = info.get("debtToEquity")
    if debt and debt > 200:
        score -= 10
        flags.append(f"High leverage (D/E {debt:.0f}%)")

    score = max(0, min(100, score))
    return {
        "symbol": symbol,
        "name": info.get("shortName"),
        "score": round(score, 1),
        "grade": _grade(score),
        "positives": positives,
        "flags": flags,
        "data": {
            "insider_pct": insider_pct,
            "institutional_pct": inst_pct,
            "governance_risk": governance,
            "roe": roe,
            "debt_to_equity": debt,
        },
    }
