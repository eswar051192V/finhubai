"""
Position Sizing Engine — Kelly Criterion, ATR-based sizing,
and portfolio concentration checks.
"""
from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

log = logging.getLogger(__name__)


def kelly_criterion(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    fraction: float = 0.5,
) -> dict[str, Any]:
    """
    Half-Kelly (default) position sizing.
    win_rate: probability of winning (0-1)
    avg_win/avg_loss: average P&L per trade (positive values)
    fraction: Kelly fraction (0.5 = half-Kelly for safety)
    """
    if avg_loss == 0:
        return {"error": "avg_loss cannot be zero"}
    b = avg_win / avg_loss
    p = win_rate
    q = 1 - p
    full_kelly = (b * p - q) / b
    adjusted = full_kelly * fraction
    return {
        "full_kelly_pct": round(full_kelly * 100, 2),
        "adjusted_kelly_pct": round(max(0, adjusted) * 100, 2),
        "fraction_used": fraction,
        "win_rate": win_rate,
        "payoff_ratio": round(b, 2),
        "recommendation": (
            "DO NOT TRADE" if adjusted <= 0
            else f"Allocate {adjusted * 100:.1f}% of capital"
        ),
    }


def atr_position_size(
    symbol: str,
    capital: float,
    risk_pct: float = 0.02,
    atr_multiplier: float = 2.0,
    period: str = "3mo",
) -> dict[str, Any]:
    """
    ATR-based position sizing.
    risk_pct: max capital to risk per trade (default 2%)
    atr_multiplier: stop loss distance = ATR * multiplier
    """
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period)
        if hist is None or len(hist) < 14:
            return {"error": "insufficient price history"}

        high = hist["High"]
        low = hist["Low"]
        close = hist["Close"]
        tr = []
        for i in range(1, len(hist)):
            tr.append(max(
                high.iloc[i] - low.iloc[i],
                abs(high.iloc[i] - close.iloc[i - 1]),
                abs(low.iloc[i] - close.iloc[i - 1]),
            ))
        atr = sum(tr[-14:]) / 14
        last_price = float(close.iloc[-1])
        risk_amount = capital * risk_pct
        stop_distance = atr * atr_multiplier
        if stop_distance <= 0:
            return {"error": "ATR is zero"}
        shares = int(risk_amount / stop_distance)
        position_value = shares * last_price

        return {
            "symbol": symbol,
            "last_price": round(last_price, 2),
            "atr_14": round(atr, 2),
            "stop_distance": round(stop_distance, 2),
            "stop_loss_price": round(last_price - stop_distance, 2),
            "risk_amount": round(risk_amount, 2),
            "shares": shares,
            "position_value": round(position_value, 2),
            "position_pct": round((position_value / capital) * 100, 2),
            "capital": capital,
            "risk_pct": risk_pct,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def portfolio_concentration_check(
    holdings: list[dict[str, Any]],
    max_single_pct: float = 20.0,
    max_sector_pct: float = 40.0,
) -> dict[str, Any]:
    """
    Check portfolio concentration.
    holdings: list of {symbol, value, sector?}
    """
    total = sum(h.get("value", 0) for h in holdings)
    if total == 0:
        return {"error": "empty portfolio"}

    warnings = []
    sector_totals: dict[str, float] = {}
    positions = []
    for h in holdings:
        pct = (h["value"] / total) * 100
        positions.append({
            "symbol": h["symbol"],
            "value": h["value"],
            "pct": round(pct, 2),
        })
        if pct > max_single_pct:
            warnings.append(
                f"{h['symbol']} is {pct:.1f}% of portfolio "
                f"(limit: {max_single_pct}%)"
            )
        sector = h.get("sector", "Unknown")
        sector_totals[sector] = sector_totals.get(sector, 0) + h["value"]

    sector_pcts = {
        s: round((v / total) * 100, 2) for s, v in sector_totals.items()
    }
    for s, pct in sector_pcts.items():
        if pct > max_sector_pct:
            warnings.append(
                f"Sector '{s}' is {pct:.1f}% of portfolio "
                f"(limit: {max_sector_pct}%)"
            )
    n_eff = 0
    for h in holdings:
        w = h["value"] / total
        if w > 0:
            n_eff += w * w
    n_eff = round(1 / n_eff, 1) if n_eff > 0 else 0

    return {
        "total_value": round(total, 2),
        "positions": positions,
        "sector_breakdown": sector_pcts,
        "effective_n": n_eff,
        "warnings": warnings,
        "healthy": len(warnings) == 0,
    }
