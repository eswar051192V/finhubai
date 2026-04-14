# ruff: noqa: E501
"""
GO/NO-GO Signal Engine — composite scoring 0-100.
Combines valuation, technicals, fundamentals, sentiment, option chain,
and macro signals into a clear recommendation.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import yfinance as yf

log = logging.getLogger(__name__)

SIGNAL_LABELS = {
    (80, 101): "STRONG GO",
    (60, 80): "GO",
    (40, 60): "BORDERLINE",
    (20, 40): "NO-GO",
    (0, 20): "STRONG NO-GO",
}

DEFAULT_WEIGHTS = {
    "valuation": 0.20,
    "technicals": 0.20,
    "fundamentals": 0.15,
    "sentiment": 0.15,
    "option_chain": 0.15,
    "macro": 0.15,
}


def _score_label(score: float) -> str:
    for (lo, hi), label in SIGNAL_LABELS.items():
        if lo <= score < hi:
            return label
    return "UNKNOWN"


def _valuation_score(info: dict) -> dict[str, Any]:
    pe = info.get("trailingPE")
    pb = info.get("priceToBook")
    score = 50.0
    reasons = []
    if pe is not None:
        if pe < 15:
            score += 20
            reasons.append(f"P/E {pe:.1f} (cheap)")
        elif pe < 25:
            score += 5
            reasons.append(f"P/E {pe:.1f} (fair)")
        elif pe < 40:
            score -= 10
            reasons.append(f"P/E {pe:.1f} (expensive)")
        else:
            score -= 25
            reasons.append(f"P/E {pe:.1f} (very expensive)")
    if pb is not None:
        if pb < 2:
            score += 10
            reasons.append(f"P/B {pb:.1f} (attractive)")
        elif pb > 5:
            score -= 10
            reasons.append(f"P/B {pb:.1f} (premium)")
    return {"score": max(0, min(100, score)), "reasons": reasons}


def _technicals_score(info: dict, last: Optional[float]) -> dict[str, Any]:
    score = 50.0
    reasons = []
    high52 = info.get("fiftyTwoWeekHigh")
    low52 = info.get("fiftyTwoWeekLow")
    sma50 = info.get("fiftyDayAverage")
    sma200 = info.get("twoHundredDayAverage")
    if last and high52 and low52 and high52 != low52:
        pos = (last - low52) / (high52 - low52)
        if pos > 0.9:
            score -= 15
            reasons.append("Near 52-week high (overbought risk)")
        elif pos < 0.2:
            score += 15
            reasons.append("Near 52-week low (potential value)")
        else:
            score += 5
            reasons.append(f"52w range position: {pos:.0%}")
    if last and sma50:
        if last > sma50:
            score += 10
            reasons.append("Price above 50-day SMA (bullish)")
        else:
            score -= 10
            reasons.append("Price below 50-day SMA (bearish)")
    if sma50 and sma200:
        if sma50 > sma200:
            score += 10
            reasons.append("Golden cross (50 > 200 SMA)")
        else:
            score -= 10
            reasons.append("Death cross (50 < 200 SMA)")
    return {"score": max(0, min(100, score)), "reasons": reasons}


def _fundamentals_score(info: dict) -> dict[str, Any]:
    score = 50.0
    reasons = []
    roe = info.get("returnOnEquity")
    margin = info.get("profitMargins")
    rev_growth = info.get("revenueGrowth")
    if roe is not None:
        if roe > 0.20:
            score += 15
            reasons.append(f"ROE {roe:.0%} (excellent)")
        elif roe > 0.10:
            score += 5
            reasons.append(f"ROE {roe:.0%} (good)")
        elif roe < 0:
            score -= 20
            reasons.append(f"ROE {roe:.0%} (negative)")
    if margin is not None:
        if margin > 0.20:
            score += 10
            reasons.append(f"Profit margin {margin:.0%} (strong)")
        elif margin < 0:
            score -= 15
            reasons.append(f"Profit margin {margin:.0%} (loss-making)")
    if rev_growth is not None:
        if rev_growth > 0.15:
            score += 10
            reasons.append(f"Revenue growth {rev_growth:.0%} (high)")
        elif rev_growth < 0:
            score -= 10
            reasons.append(f"Revenue growth {rev_growth:.0%} (declining)")
    return {"score": max(0, min(100, score)), "reasons": reasons}


def compute_gonogo(
    symbol: str,
    sentiment_score: Optional[float] = None,
    option_chain_score: Optional[float] = None,
    macro_score: Optional[float] = None,
    weights: Optional[dict[str, float]] = None,
) -> dict[str, Any]:
    """
    Compute composite GO/NO-GO score for a symbol.
    External scores (sentiment, option_chain, macro) can be passed in or default to 50.
    """
    w = weights or DEFAULT_WEIGHTS
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

    last = info.get("currentPrice") or info.get("regularMarketPrice")
    val = _valuation_score(info)
    tech = _technicals_score(info, last)
    fund = _fundamentals_score(info)

    sent = {"score": sentiment_score if sentiment_score is not None else 50.0, "reasons": []}
    oc = {"score": option_chain_score if option_chain_score is not None else 50.0, "reasons": []}
    mac = {"score": macro_score if macro_score is not None else 50.0, "reasons": []}

    composite = (
        val["score"] * w.get("valuation", 0.2)
        + tech["score"] * w.get("technicals", 0.2)
        + fund["score"] * w.get("fundamentals", 0.15)
        + sent["score"] * w.get("sentiment", 0.15)
        + oc["score"] * w.get("option_chain", 0.15)
        + mac["score"] * w.get("macro", 0.15)
    )
    composite = round(max(0, min(100, composite)), 1)

    return {
        "symbol": symbol,
        "composite_score": composite,
        "signal": _score_label(composite),
        "last_price": last,
        "breakdown": {
            "valuation": val,
            "technicals": tech,
            "fundamentals": fund,
            "sentiment": sent,
            "option_chain": oc,
            "macro": mac,
        },
        "weights": w,
    }
