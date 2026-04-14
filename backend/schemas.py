from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class BrokerId(str, Enum):
    zerodha = "zerodha"
    upstox = "upstox"
    hdfc_sky = "hdfc_sky"
    angel_one = "angel_one"
    ibkr = "ibkr"


class Segment(str, Enum):
    equity_delivery = "equity_delivery"
    equity_intraday = "equity_intraday"
    futures = "futures"
    options = "options"


class Side(str, Enum):
    buy = "buy"
    sell = "sell"


class CostCalculatorRequest(BaseModel):
    broker: BrokerId
    segment: Segment
    side: Side
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    premium: Optional[float] = Field(default=None, description="Option premium per unit (options only)")
    is_itm_near_expiry: bool = False


class WhenToSellRequest(BaseModel):
    purchase_date: date
    as_of: Optional[date] = None
    buy_price: float = Field(gt=0)
    last_price: float = Field(gt=0)
    quantity: float = Field(gt=0)


class HealthDepsResponse(BaseModel):
    database: bool
    redis: bool


class ApiError(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# ---------------------------------------------------------------------------
# Markets schemas
# ---------------------------------------------------------------------------


class MarketCategory(str, Enum):
    # Curated
    india_equity = "india_equity"
    india_mf = "india_mf"
    india_bonds = "india_bonds"
    india_index = "india_index"
    energy = "energy"
    commodities = "commodities"
    forex = "forex"
    us_equity = "us_equity"
    us_options = "us_options"
    crypto = "crypto"
    us_bonds = "us_bonds"
    us_futures = "us_futures"
    real_estate = "real_estate"
    # Extended (full downloaded universe)
    india_equity_all = "india_equity_all"
    bse_equity = "bse_equity"
    india_mf_all = "india_mf_all"
    india_fno = "india_fno"
    crypto_all = "crypto_all"
    forex_all = "forex_all"
    metals_all = "metals_all"
    real_estate_all = "real_estate_all"


class InstrumentQuote(BaseModel):
    symbol: str
    name: Optional[str] = None
    sub_category: Optional[str] = None
    last: Optional[float] = None
    currency: Optional[str] = None
    prev_close: Optional[float] = None
    change_pct: Optional[float] = None
    error: Optional[str] = None


class CategoryResponse(BaseModel):
    category: str
    count: int
    instruments: list[InstrumentQuote]


class CategoryInfo(BaseModel):
    id: str
    label: str
    count: int


class PulseItem(BaseModel):
    id: str
    symbol: str
    last: Optional[float] = None
    change_pct: Optional[float] = None
    currency: Optional[str] = None


class GlobalPulseResponse(BaseModel):
    pulse: list[PulseItem]


class SearchResult(BaseModel):
    symbol: str
    name: str
    category: str
    sub_category: Optional[str] = None


class MetalCityPrice(BaseModel):
    city: str
    gold_24k_per_10g: float
    gold_22k_per_10g: float
    silver_per_kg: float
    premium_inr: float


class MetalReference(BaseModel):
    gold_usd_per_oz: float
    silver_usd_per_oz: float
    usdinr: float
    gold_inr_per_10g_base: float


class MetalPricesResponse(BaseModel):
    reference: Optional[MetalReference] = None
    cities: Optional[list[MetalCityPrice]] = None
    error: Optional[str] = None


class InstrumentDetail(BaseModel):
    symbol: str
    last: Optional[float] = None
    currency: Optional[str] = None
    name: Optional[str] = None
    exchange: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    high_52w: Optional[float] = Field(None, alias="52w_high")
    low_52w: Optional[float] = Field(None, alias="52w_low")
    volume: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    error: Optional[str] = None

    model_config = {"populate_by_name": True}
