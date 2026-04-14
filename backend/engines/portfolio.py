"""
Portfolio Risk Dashboard — correlation, stress testing, and allocation.
Also handles long-term goal tracking (retirement, SIP).
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


def portfolio_risk(
    holdings: list[dict[str, Any]],
    period: str = "1y",
) -> dict[str, Any]:
    """
    Compute portfolio risk metrics: correlation matrix, volatility,
    stress scenarios, and diversification score.
    holdings: [{symbol, weight}]
    """
    if not holdings:
        return {"error": "empty portfolio"}

    symbols = [h["symbol"] for h in holdings]
    weights_raw = [h.get("weight", 1.0 / len(holdings)) for h in holdings]
    total_w = sum(weights_raw)
    weights = np.array([w / total_w for w in weights_raw])

    try:
        data = yf.download(symbols, period=period, progress=False)
        if data is None or data.empty:
            return {"error": "no price data available"}

        if "Close" in data.columns:
            close = data["Close"]
        else:
            close = data

        if isinstance(close, pd.Series):
            close = close.to_frame(name=symbols[0])

        returns = close.pct_change().dropna()
        if returns.empty:
            return {"error": "insufficient return data"}

        cov_matrix = returns.cov().values * 252
        corr_matrix = returns.corr()

        port_var = float(weights @ cov_matrix @ weights)
        port_vol = float(np.sqrt(port_var))
        ann_returns = returns.mean() * 252
        port_return = float(weights @ ann_returns.values)
        sharpe = port_return / port_vol if port_vol > 0 else 0

        stress = {}
        for scenario, shock in [
            ("market_10pct_drop", -0.10),
            ("market_20pct_drop", -0.20),
            ("market_30pct_crash", -0.30),
        ]:
            betas = []
            market_ret = returns.mean(axis=1)
            for sym in symbols:
                if sym in returns.columns:
                    cov_sm = np.cov(returns[sym], market_ret)[0, 1]
                    var_m = np.var(market_ret)
                    beta = cov_sm / var_m if var_m > 0 else 1.0
                    betas.append(beta)
                else:
                    betas.append(1.0)
            betas = np.array(betas)
            port_impact = float(weights @ (betas * shock))
            stress[scenario] = round(port_impact * 100, 2)

        corr_data = {}
        for i, s1 in enumerate(symbols):
            if s1 in corr_matrix.index:
                for j, s2 in enumerate(symbols):
                    if s2 in corr_matrix.columns:
                        corr_data[f"{s1}:{s2}"] = round(
                            float(corr_matrix.loc[s1, s2]), 3
                        )

        return {
            "annual_return_pct": round(port_return * 100, 2),
            "annual_volatility_pct": round(port_vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "stress_scenarios": stress,
            "correlation": corr_data,
            "symbols": symbols,
            "weights": [round(float(w), 4) for w in weights],
        }
    except Exception as e:
        log.exception("Portfolio risk computation failed")
        return {"error": str(e)}


def retirement_tracker(
    current_age: int,
    retirement_age: int,
    current_corpus: float,
    monthly_sip: float,
    expected_return_pct: float = 12.0,
    inflation_pct: float = 6.0,
    target_monthly_expense: float = 100000,
) -> dict[str, Any]:
    """
    Simple retirement corpus projection with SIP and inflation.
    """
    years = retirement_age - current_age
    if years <= 0:
        return {"error": "already at or past retirement age"}

    r = expected_return_pct / 100 / 12
    n = years * 12
    sip_fv = monthly_sip * (((1 + r) ** n - 1) / r) * (1 + r)
    lump_fv = current_corpus * (1 + expected_return_pct / 100) ** years
    total_corpus = sip_fv + lump_fv

    real_return = (expected_return_pct - inflation_pct) / 100
    monthly_need_at_retirement = target_monthly_expense * (
        (1 + inflation_pct / 100) ** years
    )
    annual_need = monthly_need_at_retirement * 12
    corpus_needed = annual_need / real_return if real_return > 0 else annual_need * 30

    return {
        "years_to_retirement": years,
        "projected_corpus": round(total_corpus, 0),
        "corpus_needed": round(corpus_needed, 0),
        "surplus_or_deficit": round(total_corpus - corpus_needed, 0),
        "on_track": total_corpus >= corpus_needed,
        "monthly_need_at_retirement": round(monthly_need_at_retirement, 0),
        "sip_future_value": round(sip_fv, 0),
        "lump_sum_future_value": round(lump_fv, 0),
        "assumptions": {
            "expected_return_pct": expected_return_pct,
            "inflation_pct": inflation_pct,
            "monthly_sip": monthly_sip,
        },
    }
