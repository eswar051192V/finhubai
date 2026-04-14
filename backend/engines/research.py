"""
Research Engine — thesis evaluation, bull/base/bear scenario
analysis, and evidence gathering.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

import yfinance as yf

log = logging.getLogger(__name__)


def evaluate_thesis(
    symbol: str,
    thesis: str,
    thesis_type: str = "bullish",
    target_price: Optional[float] = None,
    timeframe_months: int = 12,
) -> dict[str, Any]:
    """
    Cross-reference a user's thesis against available data.
    Returns supporting/contradicting evidence plus bull/base/bear scenarios.
    """
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

    current = info.get("currentPrice") or info.get("regularMarketPrice")
    supporting: list[str] = []
    contradicting: list[str] = []

    pe = info.get("trailingPE")
    roe = info.get("returnOnEquity")
    rev_growth = info.get("revenueGrowth")
    debt_eq = info.get("debtToEquity")
    analyst_target = info.get("targetMeanPrice")

    if thesis_type == "bullish":
        if rev_growth and rev_growth > 0.10:
            supporting.append(f"Revenue growing at {rev_growth:.0%}")
        elif rev_growth and rev_growth < 0:
            contradicting.append(f"Revenue declining at {rev_growth:.0%}")
        if roe and roe > 0.15:
            supporting.append(f"Strong ROE at {roe:.0%}")
        elif roe and roe < 0.05:
            contradicting.append(f"Weak ROE at {roe:.0%}")
        if pe and pe > 50:
            contradicting.append(f"High P/E of {pe:.1f} — expensive")
        if debt_eq and debt_eq > 150:
            contradicting.append(f"High debt-to-equity: {debt_eq:.0f}%")
    else:
        if rev_growth and rev_growth < 0:
            supporting.append("Revenue declining confirms bearish view")
        if pe and pe > 50:
            supporting.append(f"Overvalued at P/E {pe:.1f}")

    scenarios = {
        "bull": {
            "description": "Strong execution, market tailwinds",
            "target": round(current * 1.30, 2) if current else None,
            "probability": "30%",
        },
        "base": {
            "description": "In-line with expectations",
            "target": analyst_target or (round(current * 1.10, 2) if current else None),
            "probability": "50%",
        },
        "bear": {
            "description": "Earnings miss, macro headwinds",
            "target": round(current * 0.80, 2) if current else None,
            "probability": "20%",
        },
    }

    thesis_score = 50 + len(supporting) * 10 - len(contradicting) * 10
    thesis_score = max(0, min(100, thesis_score))

    return {
        "symbol": symbol,
        "thesis": thesis,
        "thesis_type": thesis_type,
        "thesis_score": thesis_score,
        "current_price": current,
        "target_price": target_price,
        "timeframe_months": timeframe_months,
        "supporting_evidence": supporting,
        "contradicting_evidence": contradicting,
        "scenarios": scenarios,
        "timestamp": datetime.now().isoformat(),
    }
