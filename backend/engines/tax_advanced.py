# ruff: noqa: E501
"""
Advanced Tax Engine — multi-country, cumulative tax bill,
tax-loss harvesting, and CA export package.
Covers India (full), US (India-resident), basic UK/EU.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Optional

log = logging.getLogger(__name__)


class Country(str, Enum):
    INDIA = "IN"
    US = "US"
    UK = "UK"
    GERMANY = "DE"


class InstrumentType(str, Enum):
    EQUITY_DELIVERY = "equity_delivery"
    EQUITY_INTRADAY = "equity_intraday"
    FUTURES = "futures"
    OPTIONS = "options"
    MUTUAL_FUND = "mutual_fund"
    DEBT_MF = "debt_mf"
    CRYPTO = "crypto"
    US_EQUITY = "us_equity"
    US_OPTION = "us_option"
    UK_EQUITY = "uk_equity"
    REIT = "reit"
    BOND = "bond"


class TaxTreatment(str, Enum):
    INDIA_STCG_EQUITY = "india_stcg_equity"
    INDIA_LTCG_EQUITY = "india_ltcg_equity"
    INDIA_BUSINESS_FO = "india_business_fo"
    INDIA_SPECULATIVE = "india_speculative"
    INDIA_DEBT = "india_debt"
    INDIA_CRYPTO = "india_crypto"
    US_STCG = "us_stcg"
    US_LTCG = "us_ltcg"
    UK_CGT = "uk_cgt"
    EXEMPT = "exempt"


@dataclass
class Transaction:
    symbol: str
    instrument_type: InstrumentType
    country: Country
    action: str  # buy, sell, dividend, expiry, etc.
    quantity: float
    price: float
    date: date
    currency: str = "INR"
    fx_rate: float = 1.0
    charges: float = 0.0
    notes: str = ""


@dataclass
class TaxResult:
    treatment: TaxTreatment
    gross_gain: float
    tax_amount: float
    effective_rate: float
    breakdown: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


# ── India Tax Rates (FY 2024-25) ─────────────────────────────

INDIA_RATES = {
    "stcg_equity": 0.20,
    "ltcg_equity": 0.125,
    "ltcg_exemption": 125_000,
    "ltcg_holding_days": 365,
    "crypto_flat": 0.30,
    "fo_slab_indicative": 0.30,
    "surcharge_tiers": [
        (5_000_000, 0.10),
        (10_000_000, 0.15),
        (20_000_000, 0.25),
        (50_000_000, 0.37),
    ],
    "cess": 0.04,
}


def _india_surcharge(income: float) -> float:
    rate = 0.0
    for threshold, sur in INDIA_RATES["surcharge_tiers"]:
        if income > threshold:
            rate = sur
    return rate


def classify_india_transaction(
    txn: Transaction,
    buy_date: Optional[date] = None,
) -> TaxTreatment:
    """Classify an India transaction into the correct tax treatment."""
    if txn.instrument_type == InstrumentType.CRYPTO:
        return TaxTreatment.INDIA_CRYPTO
    if txn.instrument_type == InstrumentType.EQUITY_INTRADAY:
        return TaxTreatment.INDIA_SPECULATIVE
    if txn.instrument_type in (InstrumentType.FUTURES, InstrumentType.OPTIONS):
        return TaxTreatment.INDIA_BUSINESS_FO
    if txn.instrument_type in (InstrumentType.DEBT_MF, InstrumentType.BOND):
        return TaxTreatment.INDIA_DEBT
    if txn.instrument_type in (
        InstrumentType.EQUITY_DELIVERY,
        InstrumentType.MUTUAL_FUND,
        InstrumentType.REIT,
    ):
        if buy_date:
            days = (txn.date - buy_date).days
            if days > INDIA_RATES["ltcg_holding_days"]:
                return TaxTreatment.INDIA_LTCG_EQUITY
        return TaxTreatment.INDIA_STCG_EQUITY
    return TaxTreatment.INDIA_STCG_EQUITY


def compute_india_tax(
    gain: float,
    treatment: TaxTreatment,
    total_income: float = 0,
    ltcg_used: float = 0,
) -> TaxResult:
    """Compute India tax on a gain."""
    if treatment == TaxTreatment.INDIA_CRYPTO:
        tax = gain * INDIA_RATES["crypto_flat"] if gain > 0 else 0
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=0.30,
            notes=["30% flat on crypto, no loss offset allowed"],
        )
    if treatment == TaxTreatment.INDIA_SPECULATIVE:
        tax = gain * INDIA_RATES["fo_slab_indicative"] if gain > 0 else 0
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=INDIA_RATES["fo_slab_indicative"],
            notes=["Speculative income — slab rate, offset speculative only"],
        )
    if treatment == TaxTreatment.INDIA_BUSINESS_FO:
        tax = gain * INDIA_RATES["fo_slab_indicative"] if gain > 0 else 0
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=INDIA_RATES["fo_slab_indicative"],
            notes=["F&O business income — slab rate"],
        )
    if treatment == TaxTreatment.INDIA_LTCG_EQUITY:
        taxable = max(0, gain - max(0, INDIA_RATES["ltcg_exemption"] - ltcg_used))
        tax = taxable * INDIA_RATES["ltcg_equity"]
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=round(tax / gain, 4) if gain > 0 else 0,
            breakdown={"exemption_used": min(gain, INDIA_RATES["ltcg_exemption"] - ltcg_used), "taxable": taxable},
            notes=[f"LTCG 12.5% above ₹{INDIA_RATES['ltcg_exemption']:,.0f} exemption"],
        )
    if treatment == TaxTreatment.INDIA_STCG_EQUITY:
        tax = gain * INDIA_RATES["stcg_equity"] if gain > 0 else 0
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=INDIA_RATES["stcg_equity"],
            notes=["STCG 20% on listed equity"],
        )
    if treatment == TaxTreatment.INDIA_DEBT:
        tax = gain * INDIA_RATES["fo_slab_indicative"] if gain > 0 else 0
        return TaxResult(
            treatment=treatment,
            gross_gain=gain,
            tax_amount=round(tax, 2),
            effective_rate=INDIA_RATES["fo_slab_indicative"],
            notes=["Debt MF — slab rate (post Apr 2023, no indexation)"],
        )
    return TaxResult(treatment=treatment, gross_gain=gain, tax_amount=0, effective_rate=0)


def us_tax_india_resident(
    gain_usd: float,
    holding_days: int,
    dividend_usd: float = 0,
    fx_rate: float = 83.5,
) -> dict[str, Any]:
    """US tax calculation for India-resident investors."""
    us_withholding = round(dividend_usd * 0.25, 2)
    gain_inr = gain_usd * fx_rate
    dividend_inr = dividend_usd * fx_rate

    if holding_days > 730:
        treatment = "LTCG (>24 months) — 12.5%"
        gain_tax = gain_inr * 0.125 if gain_inr > 0 else 0
    else:
        treatment = "STCG (<24 months) — 20%"
        gain_tax = gain_inr * 0.20 if gain_inr > 0 else 0

    div_tax_india = dividend_inr * 0.30
    ftc_available = us_withholding * fx_rate
    net_div_tax = max(0, div_tax_india - ftc_available)

    return {
        "gain_usd": gain_usd,
        "gain_inr": round(gain_inr, 2),
        "treatment": treatment,
        "gain_tax_inr": round(gain_tax, 2),
        "dividend_usd": dividend_usd,
        "us_withholding_usd": us_withholding,
        "ftc_inr": round(ftc_available, 2),
        "dividend_tax_india_inr": round(div_tax_india, 2),
        "net_dividend_tax_inr": round(net_div_tax, 2),
        "total_tax_inr": round(gain_tax + net_div_tax, 2),
        "fx_rate": fx_rate,
        "notes": [
            "File Form 67 BEFORE filing ITR to claim FTC",
            "US CG exempt under DTAA — only India taxes apply",
        ],
    }


def tax_loss_harvest_scan(
    positions: list[dict[str, Any]],
    min_loss_inr: float = 5000,
) -> list[dict[str, Any]]:
    """
    Scan positions for tax-loss harvesting opportunities.
    India advantage: no wash-sale rule.
    positions: [{symbol, buy_price, current_price, quantity, buy_date, instrument_type}]
    """
    opportunities = []
    for p in positions:
        buy = p.get("buy_price", 0)
        current = p.get("current_price", 0)
        qty = p.get("quantity", 0)
        unrealized = (current - buy) * qty
        if unrealized < -min_loss_inr:
            buy_date = p.get("buy_date")
            days_held = 0
            if buy_date:
                if isinstance(buy_date, str):
                    buy_date = date.fromisoformat(buy_date)
                days_held = (date.today() - buy_date).days

            is_stcg = days_held <= 365
            tax_rate = 0.20 if is_stcg else 0.125
            tax_saved = abs(unrealized) * tax_rate

            opportunities.append({
                "symbol": p["symbol"],
                "unrealized_loss": round(unrealized, 2),
                "tax_saved_estimate": round(tax_saved, 2),
                "days_held": days_held,
                "loss_type": "STCG" if is_stcg else "LTCG",
                "action": f"Sell to book ₹{abs(unrealized):,.0f} loss → save ~₹{tax_saved:,.0f} tax",
                "note": "India has no wash-sale rule — can rebuy immediately",
            })
    opportunities.sort(key=lambda x: x["tax_saved_estimate"], reverse=True)
    return opportunities


def cumulative_tax_bill(
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Aggregate multiple transactions into a cumulative tax summary.
    Each txn: {gain, treatment, ...}
    """
    by_treatment: dict[str, float] = {}
    total_gain = 0.0
    total_tax = 0.0
    ltcg_used = 0.0

    for txn in transactions:
        gain = txn.get("gain", 0)
        treatment = txn.get("treatment", "india_stcg_equity")
        try:
            tt = TaxTreatment(treatment)
        except ValueError:
            tt = TaxTreatment.INDIA_STCG_EQUITY

        result = compute_india_tax(gain, tt, ltcg_used=ltcg_used)
        if tt == TaxTreatment.INDIA_LTCG_EQUITY and gain > 0:
            ltcg_used += min(gain, INDIA_RATES["ltcg_exemption"] - ltcg_used)

        total_gain += gain
        total_tax += result.tax_amount
        by_treatment[treatment] = by_treatment.get(treatment, 0) + result.tax_amount

    return {
        "total_gain": round(total_gain, 2),
        "total_tax": round(total_tax, 2),
        "effective_rate": round(total_tax / total_gain, 4) if total_gain > 0 else 0,
        "by_treatment": {k: round(v, 2) for k, v in by_treatment.items()},
        "advance_tax_schedule": {
            "q1_jun15": round(total_tax * 0.15, 2),
            "q2_sep15": round(total_tax * 0.45, 2),
            "q3_dec15": round(total_tax * 0.75, 2),
            "q4_mar15": round(total_tax, 2),
        },
    }
