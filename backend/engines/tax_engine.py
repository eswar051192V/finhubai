"""India-listed equity basics: STCG/LTCG hold analysis and F&O turnover alerts."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from backend.config import get_settings


def _days_held(purchase: date, as_of: date) -> int:
    return max(0, (as_of - purchase).days)


def classify_equity_gain(
    purchase_date: date,
    as_of: date,
    buy_price: float,
    last_price: float,
    quantity: float,
) -> dict[str, Any]:
    settings = get_settings()
    days = _days_held(purchase_date, as_of)
    is_long_term = days >= settings.india_ltcg_holding_days
    pnl = (last_price - buy_price) * quantity
    pnl_pct = ((last_price / buy_price) - 1.0) * 100 if buy_price else 0.0

    if pnl <= 0:
        treatment = "loss"
        est_tax = 0.0
    elif is_long_term:
        treatment = "ltcg_equity"
        gain = pnl
        taxable = max(0.0, gain - settings.india_ltcg_equity_exemption_inr)
        est_tax = taxable * settings.india_ltcg_equity_rate
    else:
        treatment = "stcg_equity"
        est_tax = pnl * settings.india_stcg_equity_rate

    return {
        "days_held": days,
        "is_long_term": is_long_term,
        "treatment": treatment,
        "notional_pnl": round(pnl, 2),
        "notional_pnl_pct": round(pnl_pct, 2),
        "estimated_tax_inr": round(est_tax, 2),
        "rates": {
            "stcg_equity": settings.india_stcg_equity_rate,
            "ltcg_equity": settings.india_ltcg_equity_rate,
            "ltcg_exemption_inr": settings.india_ltcg_equity_exemption_inr,
            "ltcg_min_days": settings.india_ltcg_holding_days,
        },
    }


def when_to_sell_analysis(
    purchase_date: date,
    as_of: date | None,
    buy_price: float,
    last_price: float,
    quantity: float,
) -> dict[str, Any]:
    settings = get_settings()
    as_of = as_of or date.today()
    snap = classify_equity_gain(purchase_date, as_of, buy_price, last_price, quantity)
    days = snap["days_held"]
    remaining = max(0, settings.india_ltcg_holding_days - days)

    if snap["notional_pnl"] <= 0:
        recommendation = "No tax on gains; consider risk management rather than tax timing."
    elif snap["is_long_term"]:
        recommendation = "Already long-term for listed equity (>=365 days). LTCG rules apply."
    else:
        target = purchase_date + timedelta(days=settings.india_ltcg_holding_days)
        recommendation = (
            f"Hold at least {remaining} more calendar days (until {target.isoformat()}) "
            "to move from STCG to LTCG treatment for listed equity (model assumption)."
        )

    return {
        **snap,
        "as_of": as_of.isoformat(),
        "recommendation": recommendation,
        "days_to_ltcg": remaining if not snap["is_long_term"] else 0,
    }


def itm_option_expiry_stt_warning(
    intrinsic_value_per_unit: float,
    quantity: float,
    *,
    stt_rate: float | None = None,
) -> dict[str, Any]:
    """Rough STT on exercise-style taxation — verify against contract and current STT schedule."""
    settings = get_settings()
    rate = stt_rate if stt_rate is not None else settings.india_stt_option_sell_on_exercise_pct
    notional = max(0.0, intrinsic_value_per_unit) * quantity
    est_stt = notional * rate
    return {
        "estimated_stt_inr": round(est_stt, 2),
        "stt_rate_used": rate,
        "note": "ITM expiry can change tax/STT outcomes vs closing before expiry. Verify with broker statement.",
    }


def fo_turnover_alert(turnover_ytd_inr: float) -> dict[str, Any]:
    settings = get_settings()
    threshold = settings.india_fo_audit_turnover_inr
    return {
        "turnover_ytd_inr": turnover_ytd_inr,
        "audit_threshold_inr": threshold,
        "requires_audit_attention": turnover_ytd_inr >= threshold,
        "note": "ICAI F&O turnover/audit tests are nuanced; this is a simple threshold flag only.",
    }
