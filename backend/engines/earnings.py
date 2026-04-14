"""
Earnings Intelligence — tracks upcoming earnings,
provides pre-earnings analysis and strategy recommendations.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import yfinance as yf

log = logging.getLogger(__name__)


def earnings_analysis(symbol: str) -> dict[str, Any]:
    """
    Pre-earnings analysis for a stock. Fetches upcoming earnings date,
    historical surprises, and provides strategy hints.
    """
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        cal = {}
        try:
            cal = t.calendar or {}
        except Exception:
            pass

        earnings_dates = None
        try:
            ed = t.earnings_dates
            if ed is not None and not ed.empty:
                future_dates = ed[ed.index >= datetime.now()]
                if not future_dates.empty:
                    earnings_dates = [
                        str(d.date()) for d in future_dates.index[:3]
                    ]
        except Exception:
            pass

        eps_trend = info.get("earningsQuarterlyGrowth")
        rev_growth = info.get("revenueGrowth")
        analyst_target = info.get("targetMeanPrice")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        recommendation = info.get("recommendationKey", "none")

        strategy = []
        if eps_trend and eps_trend > 0.10:
            strategy.append("Strong earnings growth — consider holding through earnings")
        elif eps_trend and eps_trend < -0.10:
            strategy.append("Declining earnings — consider reducing position before report")

        if analyst_target and current_price:
            upside = ((analyst_target - current_price) / current_price) * 100
            if upside > 15:
                strategy.append(f"Analyst target implies {upside:.0f}% upside")
            elif upside < -10:
                strategy.append(f"Analyst target implies {abs(upside):.0f}% downside")

        strategy.append(
            "Options strategy: If IV > 50th percentile, consider selling premium (iron condor). "
            "If IV < 30th percentile, consider buying straddle."
        )

        return {
            "symbol": symbol,
            "name": info.get("shortName"),
            "upcoming_earnings": earnings_dates,
            "eps_quarterly_growth": eps_trend,
            "revenue_growth": rev_growth,
            "analyst_target": analyst_target,
            "current_price": current_price,
            "recommendation": recommendation,
            "strategy_hints": strategy,
            "calendar": cal,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
