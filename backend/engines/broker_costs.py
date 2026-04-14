"""
Broker all-in cost estimates (India + IBKR). Figures are **approximate** retail defaults;
verify against your contract note / tariff sheet before trading.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

GST_RATE = 0.18


class Broker(str, Enum):
    ZERODHA = "zerodha"
    UPSTOX = "upstox"
    HDFC_SKY = "hdfc_sky"
    ANGEL_ONE = "angel_one"
    IBKR = "ibkr"


class Segment(str, Enum):
    EQUITY_DELIVERY = "equity_delivery"
    EQUITY_INTRADAY = "equity_intraday"
    FUTURES = "futures"
    OPTIONS = "options"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


def _gst_on(base: float) -> float:
    return round(base * GST_RATE, 2)


def _sebi_turnover_fee(turnover: float) -> float:
    # SEBI turnover fee ~ ₹10 / crore on sell side for many segments (varies); use small placeholder
    return round(0.000001 * turnover, 2)


def _nse_exchange_equity(turnover: float, side: Side) -> float:
    # Order of0.00297% + GST baked separately — simplified flat on turnover
    rate = 0.0000297 if side == Side.BUY else 0.0000297
    return round(rate * turnover, 2)


def _stamp_delivery_buy(turnover: float) -> float:
    return max(0.0, round(0.00015 * turnover, 2))


def _zerodha_intraday_brokerage(turnover: float) -> float:
    return min(20.0, round(0.0003 * turnover, 2))


def calculate_true_cost(
    broker: Broker,
    segment: Segment,
    side: Side,
    quantity: float,
    price: float,
    *,
    premium: float | None = None,
) -> dict[str, Any]:
    """
    Returns charges in **INR** for Indian brokers; **USD** for IBKR (documented in assumptions).
    """
    if quantity <= 0 or price <= 0:
        raise ValueError("quantity and price must be positive")

    assumptions: list[str] = []
    trade_price = price if segment != Segment.OPTIONS else (premium if premium is not None else price)
    turnover = quantity * trade_price

    brokerage = stt = exchange = gst = sebi = stamp = dp = other = 0.0

    if broker == Broker.IBKR:
        # Simplified US: per-share min $0.005, assume $1 min per order for equity; options per contract
        assumptions.append("IBKR: illustrative $0.005/share, $1 minimum per order (verify tier)")
        if segment in (Segment.EQUITY_DELIVERY, Segment.EQUITY_INTRADAY):
            comm = max(1.0, 0.005 * quantity)
            brokerage = round(comm, 2)
        elif segment == Segment.OPTIONS:
            comm = max(0.65, 0.65 * max(1, quantity / 100))  # rough contract blocks
            brokerage = round(comm, 2)
        else:
            brokerage = round(max(0.85, 0.0001 * turnover), 2)
        return {
            "currency": "USD",
            "turnover": round(turnover, 2),
            "breakdown": {
                "brokerage": brokerage,
                "stt": stt,
                "exchange": exchange,
                "gst_on_charges": gst,
                "sebi": sebi,
                "stamp_duty": stamp,
                "dp_charges": dp,
                "other": other,
                "total": brokerage,
            },
            "assumptions": assumptions,
        }

    # India paths (INR)
    currency = "INR"
    exchange = _nse_exchange_equity(turnover, side)
    sebi = _sebi_turnover_fee(turnover)

    if segment == Segment.EQUITY_DELIVERY:
        if broker == Broker.ZERODHA:
            brokerage = 0.0
            stt = round(0.001 * turnover, 2) if side == Side.SELL else 0.0
            stamp = _stamp_delivery_buy(turnover) if side == Side.BUY else 0.0
            dp = 15.93 if side == Side.SELL else 0.0  # typical DP charge incl. GST (verify)
            assumptions.append("Zerodha delivery: ₹0 brokerage; STT 0.1% on sell; DP charge on sell")
        elif broker == Broker.UPSTOX:
            brokerage = 0.0
            stt = round(0.001 * turnover, 2) if side == Side.SELL else 0.0
            stamp = _stamp_delivery_buy(turnover) if side == Side.BUY else 0.0
            dp = 18.0 if side == Side.SELL else 0.0
            assumptions.append("Upstox: verify AMC/DP slabs from tariff")
        elif broker == Broker.HDFC_SKY:
            brokerage = round(0.001 * turnover, 2)  # placeholder % — user should verify
            stt = round(0.001 * turnover, 2) if side == Side.SELL else 0.0
            stamp = _stamp_delivery_buy(turnover) if side == Side.BUY else 0.0
            assumptions.append("HDFC Sky: brokerage shown as 0.1% placeholder — replace with live tariff")
        elif broker == Broker.ANGEL_ONE:
            brokerage = 0.0
            stt = round(0.001 * turnover, 2) if side == Side.SELL else 0.0
            stamp = _stamp_delivery_buy(turnover) if side == Side.BUY else 0.0
            dp = 20.0 if side == Side.SELL else 0.0
            assumptions.append("Angel One: delivery ₹0 promo common; confirm DP charge")

    elif segment == Segment.EQUITY_INTRADAY:
        stt = round(0.00025 * turnover, 2) if side == Side.SELL else 0.0
        if broker in (Broker.ZERODHA, Broker.UPSTOX, Broker.ANGEL_ONE):
            brokerage = _zerodha_intraday_brokerage(turnover)
        else:
            brokerage = round(0.0003 * turnover, 2)
        assumptions.append("Intraday STT 0.025% on sell (verify current circular)")

    elif segment == Segment.FUTURES:
        stt = round(0.0001 * turnover, 2) if side == Side.SELL else 0.0
        brokerage = _zerodha_intraday_brokerage(turnover)
        assumptions.append("F&O: flat ₹20/order style cap used where applicable")

    elif segment == Segment.OPTIONS:
        opt_turnover = quantity * (premium if premium is not None else price)
        stt = round(0.0005 * opt_turnover, 2) if side == Side.SELL else 0.0
        brokerage = 20.0
        turnover = opt_turnover
        exchange = _nse_exchange_equity(opt_turnover, side)
        sebi = _sebi_turnover_fee(opt_turnover)
        assumptions.append("Options: STT on sell 0.05% on premium; verify ITM exercise STT separately")

    pre_gst = brokerage + exchange + sebi + (dp if segment == Segment.EQUITY_DELIVERY else 0)
    gst = _gst_on(pre_gst)

    total = brokerage + stt + exchange + gst + sebi + stamp + dp + other

    return {
        "currency": currency,
        "turnover": round(turnover, 2),
        "breakdown": {
            "brokerage": round(brokerage, 2),
            "stt": round(stt, 2),
            "exchange": round(exchange, 2),
            "gst_on_charges": round(gst, 2),
            "sebi": round(sebi, 2),
            "stamp_duty": round(stamp, 2),
            "dp_charges": round(dp, 2),
            "other": round(other, 2),
            "total": round(total, 2),
        },
        "per_unit_all_in": round(total / quantity, 4),
        "assumptions": assumptions,
    }
