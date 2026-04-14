"""
Factor Model Engine — Fama-French style analysis, momentum,
sector rotation, and factor exposure.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import yfinance as yf

log = logging.getLogger(__name__)


def factor_exposure(
    symbol: str,
    benchmark: str = "^GSPC",
    period: str = "1y",
) -> dict[str, Any]:
    """
    Compute factor exposures for a stock vs benchmark.
    Returns alpha, beta, volatility, momentum, and quality metrics.
    """
    try:
        data = yf.download([symbol, benchmark], period=period, progress=False)
        if data is None or data.empty:
            return {"error": "no data"}

        close = data["Close"] if "Close" in data.columns else data
        returns = close.pct_change().dropna()

        if symbol not in returns.columns or benchmark not in returns.columns:
            return {"error": f"missing data for {symbol} or {benchmark}"}

        stock_ret = returns[symbol].values
        bench_ret = returns[benchmark].values

        beta = float(np.cov(stock_ret, bench_ret)[0, 1] / np.var(bench_ret))
        alpha_ann = float((np.mean(stock_ret) - beta * np.mean(bench_ret)) * 252)
        vol = float(np.std(stock_ret) * np.sqrt(252))
        sharpe = float(np.mean(stock_ret) * 252 / vol) if vol > 0 else 0

        # Momentum: 12-month return minus last month
        total_ret = float(np.prod(1 + stock_ret) - 1)
        last_month = float(np.prod(1 + stock_ret[-21:]) - 1) if len(stock_ret) > 21 else 0
        momentum = total_ret - last_month

        t = yf.Ticker(symbol)
        info = t.info or {}
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        roe = info.get("returnOnEquity")
        mkt_cap = info.get("marketCap")

        if mkt_cap and mkt_cap < 2e9:
            size_factor = "small_cap"
        elif mkt_cap and mkt_cap < 10e9:
            size_factor = "mid_cap"
        else:
            size_factor = "large_cap"
        value_factor = "value" if pe and pe < 15 else "growth" if pe and pe > 30 else "blend"

        return {
            "symbol": symbol,
            "alpha_annual": round(alpha_ann * 100, 2),
            "beta": round(beta, 3),
            "volatility_annual": round(vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "momentum_12m": round(total_ret * 100, 2),
            "momentum_factor": round(momentum * 100, 2),
            "size_factor": size_factor,
            "value_factor": value_factor,
            "fundamentals": {
                "pe": pe,
                "pb": pb,
                "roe": round(roe * 100, 2) if roe else None,
                "market_cap": mkt_cap,
            },
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def sector_rotation_signals(
    sectors: dict[str, str] | None = None,
    period: str = "3mo",
) -> dict[str, Any]:
    """
    Sector rotation momentum: rank sectors by recent performance.
    """
    default_sectors = {
        "XLK": "Technology", "XLF": "Financials", "XLE": "Energy",
        "XLV": "Healthcare", "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples", "XLI": "Industrials",
        "XLB": "Materials", "XLRE": "Real Estate",
        "XLC": "Communication", "XLU": "Utilities",
    }
    sector_map = sectors or default_sectors
    results = []

    for sym, name in sector_map.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period=period)
            if hist is not None and len(hist) > 1:
                ret = float((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1)
                results.append({
                    "symbol": sym,
                    "sector": name,
                    "return_pct": round(ret * 100, 2),
                })
        except Exception as e:
            log.warning("Sector rotation skip %s: %s", sym, e)

    results.sort(key=lambda x: x["return_pct"], reverse=True)
    return {
        "period": period,
        "rankings": results,
        "top_sectors": [r["sector"] for r in results[:3]],
        "bottom_sectors": [r["sector"] for r in results[-3:]],
    }


def credit_score(symbol: str) -> dict[str, Any]:
    """
    Basic credit risk analysis — Altman Z-Score approximation
    and debt coverage metrics.
    """
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        debt_eq = info.get("debtToEquity")
        current_ratio = info.get("currentRatio")
        roe = info.get("returnOnEquity")
        margin = info.get("operatingMargins")

        score = 50.0
        notes = []

        if current_ratio is not None:
            if current_ratio > 2:
                score += 15
                notes.append(f"Strong liquidity (current ratio: {current_ratio:.1f})")
            elif current_ratio < 1:
                score -= 20
                notes.append(f"Liquidity risk (current ratio: {current_ratio:.1f})")

        if debt_eq is not None:
            if debt_eq < 50:
                score += 15
                notes.append(f"Low leverage (D/E: {debt_eq:.0f}%)")
            elif debt_eq > 200:
                score -= 20
                notes.append(f"High leverage (D/E: {debt_eq:.0f}%)")

        if margin is not None:
            if margin > 0.20:
                score += 10
                notes.append(f"Strong margins ({margin:.0%})")
            elif margin < 0:
                score -= 15
                notes.append(f"Negative margins ({margin:.0%})")

        risk_level = "LOW" if score >= 70 else "MODERATE" if score >= 40 else "HIGH"

        return {
            "symbol": symbol,
            "credit_score": round(max(0, min(100, score)), 1),
            "risk_level": risk_level,
            "notes": notes,
            "metrics": {
                "debt_to_equity": debt_eq,
                "current_ratio": current_ratio,
                "roe": roe,
                "operating_margin": margin,
            },
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
