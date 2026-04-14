"""
Universe Registry — loads cached universe JSONs written by universe_loader.py
and exposes a unified, tagged CATEGORY_REGISTRY for the runtime.

Every entry is a dict: {symbol, name, sub_category, tags}
  • tags = list[str] — index memberships (NIFTY50, SENSEX…), exchange,
    instrument type, etc. Rendered as badges on the Markets UI.

This module is the single source of truth for what the UI displays. It
overlays the curated lists in markets_fetcher.py with the much bigger
downloaded universe.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_DIR = ROOT / "data" / "universe"

# Index tag → pretty label (used by UI tooltip)
INDEX_LABELS: dict[str, str] = {
    # India indices
    "NIFTY50": "Nifty 50",
    "NIFTY100": "Nifty 100",
    "NIFTY200": "Nifty 200",
    "NIFTY500": "Nifty 500",
    "NIFTYNEXT50": "Nifty Next 50",
    "NIFTYMIDCAP150": "Nifty Midcap 150",
    "NIFTYSMALLCAP250": "Nifty Smallcap 250",
    "NIFTYMICROCAP250": "Nifty Microcap 250",
    "NIFTYBANK": "Nifty Bank",
    "NIFTYIT": "Nifty IT",
    "NIFTYAUTO": "Nifty Auto",
    "NIFTYFMCG": "Nifty FMCG",
    "NIFTYPHARMA": "Nifty Pharma",
    "NIFTYMETAL": "Nifty Metal",
    "NIFTYENERGY": "Nifty Energy",
    "NIFTYREALTY": "Nifty Realty",
    "NIFTYFINSERV": "Nifty Financial Services",
    "NIFTYMEDIA": "Nifty Media",
    "NIFTYPSUBANK": "Nifty PSU Bank",
    "NIFTYPVTBANK": "Nifty Private Bank",
    "NIFTYCONSUMERDUR": "Nifty Consumer Durables",
    "NIFTYHEALTHCARE": "Nifty Healthcare",
    "NIFTYOILANDGAS": "Nifty Oil & Gas",
    "SENSEX": "BSE Sensex",
    "BSE100": "BSE 100",
    "BSE200": "BSE 200",
    "BSE500": "BSE 500",
    # US indices
    "SP500": "S&P 500",
    "NASDAQ100": "Nasdaq 100",
    "DOW30": "Dow 30",
    "SP_MIDCAP400": "S&P MidCap 400",
    "SP_SMALLCAP600": "S&P SmallCap 600",
    "RUSSELL2000": "Russell 2000",
    # GICS sectors
    "GICS_TECH": "Technology",
    "GICS_HEALTHCARE": "Healthcare",
    "GICS_FINANCIALS": "Financials",
    "GICS_CONSDISC": "Consumer Discretionary",
    "GICS_COMMSVC": "Communication Services",
    "GICS_INDUSTRIALS": "Industrials",
    "GICS_STAPLES": "Consumer Staples",
    "GICS_ENERGY": "Energy",
    "GICS_UTILITIES": "Utilities",
    "GICS_REALESTATE": "Real Estate",
    "GICS_MATERIALS": "Materials",
    # Bond families
    "TREASURY": "US Treasury",
    "GSEC": "India G-Sec",
    "SGB": "Sovereign Gold Bond",
    "GOLD_BOND": "Gold Bond",
    "YIELD": "Yield Benchmark",
    "BOND_ETF": "Bond ETF",
    "CORPORATE": "Corporate",
    "IG": "Investment Grade",
    "HY": "High Yield",
    "MUNI": "Municipal",
    "TAX_EXEMPT": "Tax-Exempt",
    "MBS": "Mortgage-Backed",
    "AGGREGATE": "Aggregate",
    "EM": "Emerging Markets",
    "TIPS": "TIPS",
    "INFLATION": "Inflation-Linked",
    "FLOATING": "Floating Rate",
    "BANK_LOAN": "Bank Loan",
    "PREFERRED": "Preferred",
    "CONVERTIBLE": "Convertible",
    "ZERO": "Zero-Coupon",
    "SHORT": "Short Duration",
    "INTERMEDIATE": "Intermediate Duration",
    "LONG": "Long Duration",
    "TARGET_MATURITY": "Target Maturity",
    "LIQUID": "Liquid",
    "PSU": "PSU",
    "SDL": "State Development Loan",
    "INTERNATIONAL": "International",
    "ACTIVE": "Active Fund",
    "USA": "USA",
    # General
    "FNO": "F&O",
    "REIT": "REIT",
    "INVIT": "InvIT",
    "ETF": "ETF",
    "PHYSICAL": "Physical",
    "INDIA": "India",
    "NSE": "NSE",
    "BSE": "BSE",
    "NYSE": "NYSE",
    "NASDAQ": "NASDAQ",
    "NYSE_AMERICAN": "NYSE American",
    "NYSE_ARCA": "NYSE Arca",
    "CBOE_BZX": "CBOE BZX",
    "IEX": "IEX",
    "AMFI": "AMFI",
    "MF": "Mutual Fund",
    "COMEX": "COMEX",
    "NYMEX": "NYMEX",
    "LME": "LME",
    "MCX": "MCX",
    "FOREX": "Forex",
    "CRYPTO": "Crypto",
    "TOP10": "Top 10",
}

# Sub-category sort order for UI (stable, predictable)
_MARKET_CAP_TIERS: dict[str, int] = {
    "NIFTY50": 0,
    "NIFTY100": 1,
    "NIFTY200": 2,
    "NIFTY500": 3,
    "NIFTYMIDCAP150": 4,
    "NIFTYSMALLCAP250": 5,
    "NIFTYMICROCAP250": 6,
}


def label_for_tag(tag: str) -> str:
    return INDEX_LABELS.get(tag, tag.replace("_", " "))


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------
def _load(name: str) -> Any:
    p = UNIVERSE_DIR / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception as e:
        log.warning("universe JSON read failed for %s: %s", name, e)
        return None


# ---------------------------------------------------------------------------
# Tag assembly
# ---------------------------------------------------------------------------
def _nse_symbol_tag_map() -> dict[str, set[str]]:
    """symbol (NSE short code, no suffix) -> set of index tags."""
    out: dict[str, set[str]] = {}
    nse_idx = _load("nse_indices.json") or {}
    for tag, symbols in nse_idx.items():
        for s in symbols:
            out.setdefault(s.upper(), set()).add(tag)
    bse_idx = _load("bse_indices.json") or {}
    for tag, symbols in bse_idx.items():
        for s in symbols:
            out.setdefault(s.upper(), set()).add(tag)
    return out


def _us_symbol_tag_map() -> dict[str, set[str]]:
    """US ticker -> set of index tags (SP500, NASDAQ100, DOW30, etc.)"""
    out: dict[str, set[str]] = {}
    us_idx = _load("us_indices.json") or {}
    for tag, symbols in us_idx.items():
        for s in symbols:
            # datahub uses BRK.B; yfinance uses BRK-B. Normalize both directions.
            key = s.replace(".", "-").upper()
            out.setdefault(key, set()).add(tag)
            out.setdefault(s.upper(), set()).add(tag)
    return out


def _sp500_sector_map() -> dict[str, str]:
    """Symbol -> GICS_XXX sector tag."""
    sp500 = _load("sp500.json") or []
    gics = {
        "Information Technology": "GICS_TECH",
        "Health Care": "GICS_HEALTHCARE",
        "Financials": "GICS_FINANCIALS",
        "Consumer Discretionary": "GICS_CONSDISC",
        "Communication Services": "GICS_COMMSVC",
        "Industrials": "GICS_INDUSTRIALS",
        "Consumer Staples": "GICS_STAPLES",
        "Energy": "GICS_ENERGY",
        "Utilities": "GICS_UTILITIES",
        "Real Estate": "GICS_REALESTATE",
        "Materials": "GICS_MATERIALS",
    }
    out: dict[str, str] = {}
    for r in sp500:
        sym = (r.get("symbol") or "").upper()
        sector = r.get("sector") or ""
        if sym and sector in gics:
            out[sym] = gics[sector]
    return out


def _fno_symbols() -> set[str]:
    fo = _load("nse_fo.json") or []
    return {(r.get("nse_symbol") or "").upper() for r in fo if r.get("nse_symbol")}


# ---------------------------------------------------------------------------
# Category builders
# ---------------------------------------------------------------------------
def build_india_equity() -> list[dict[str, Any]]:
    """NSE listed equities, tagged with their index memberships + F&O flag."""
    eq = _load("nse_equity.json") or []
    tag_map = _nse_symbol_tag_map()
    fno = _fno_symbols()
    out: list[dict[str, Any]] = []
    for row in eq:
        nse_sym = (row.get("nse_symbol") or "").upper()
        tags = {"NSE"}
        tags.update(tag_map.get(nse_sym, set()))
        if nse_sym in fno:
            tags.add("FNO")
        # Sub-category inferred from highest market-cap tier
        sub = "equity"
        best_rank = 99
        for t, rank in _MARKET_CAP_TIERS.items():
            if t in tags and rank < best_rank:
                best_rank = rank
                sub = t.lower()
        out.append(
            {
                "symbol": row["symbol"],
                "name": row.get("name") or row["symbol"],
                "sub_category": sub,
                "tags": sorted(tags),
            }
        )
    return out


def build_bse_equity() -> list[dict[str, Any]]:
    bse = _load("bse_equity.json") or []
    return [
        {
            "symbol": r["symbol"],
            "name": r.get("name") or r["symbol"],
            "sub_category": "equity",
            "tags": ["BSE"],
        }
        for r in bse
    ]


def build_india_mf() -> list[dict[str, Any]]:
    mf = _load("amfi_mf.json") or []
    out: list[dict[str, Any]] = []
    for r in mf:
        name = (r.get("name") or "").lower()
        sub = "mf"
        if "elss" in name or "tax saver" in name:
            sub = "elss"
        elif "debt" in name or "bond" in name or "gilt" in name:
            sub = "debt"
        elif "liquid" in name or "overnight" in name or "money market" in name:
            sub = "liquid"
        elif "small cap" in name:
            sub = "small_cap"
        elif "mid cap" in name or "midcap" in name:
            sub = "mid_cap"
        elif "large cap" in name or "bluechip" in name:
            sub = "large_cap"
        elif "flexi" in name or "multicap" in name or "multi cap" in name:
            sub = "flexi_cap"
        elif "hybrid" in name or "balanced" in name:
            sub = "hybrid"
        elif "index" in name or "nifty" in name or "sensex" in name:
            sub = "index"
        elif "international" in name or "global" in name or "us " in name:
            sub = "international"
        out.append(
            {
                "symbol": r["amfi_code"],
                "name": r.get("name") or r["amfi_code"],
                "sub_category": sub,
                "tags": ["AMFI", "MF"],
                "nav": r.get("nav"),
            }
        )
    return out


def build_crypto() -> list[dict[str, Any]]:
    coins = _load("crypto_top.json") or []
    return [
        {
            "symbol": c["symbol"],
            "name": c.get("name") or c["symbol"],
            "sub_category": "top100" if (c.get("market_cap_rank") or 999) <= 100 else "other",
            "tags": ["CRYPTO"] + (["TOP10"] if (c.get("market_cap_rank") or 999) <= 10 else []),
        }
        for c in coins
    ]


def build_forex() -> list[dict[str, Any]]:
    return _load("forex.json") or []


def build_metals() -> list[dict[str, Any]]:
    return (_load("metals.json") or []) + (_load("metals_india_physical.json") or [])


def build_real_estate() -> list[dict[str, Any]]:
    return _load("reits_invits.json") or []


def build_us_equity() -> list[dict[str, Any]]:
    """All US equities (NYSE + NASDAQ + AMEX) with index + GICS sector tags."""
    eq = _load("us_equity.json") or []
    idx_map = _us_symbol_tag_map()
    sector_map = _sp500_sector_map()
    out: list[dict[str, Any]] = []
    for r in eq:
        sym = (r.get("symbol") or "").upper()
        if not sym:
            continue
        tags: set[str] = set()
        exch = r.get("exchange") or ""
        if exch:
            tags.add(exch)
        if r.get("is_etf"):
            tags.add("ETF")
        tags.update(idx_map.get(sym, set()))
        sec = sector_map.get(sym)
        if sec:
            tags.add(sec)

        sub = "equity"
        if r.get("is_etf"):
            sub = "etf"
        elif "SP500" in tags:
            sub = "large_cap"
        elif "NASDAQ100" in tags:
            sub = "nasdaq100"
        elif "SP_MIDCAP400" in tags:
            sub = "mid_cap"
        elif "SP_SMALLCAP600" in tags or "RUSSELL2000" in tags:
            sub = "small_cap"

        out.append(
            {
                "symbol": sym,
                "name": r.get("name") or sym,
                "sub_category": sub,
                "tags": sorted(tags),
            }
        )
    return out


def build_india_bonds() -> list[dict[str, Any]]:
    bonds = _load("india_bonds.json") or []
    return [dict(b) for b in bonds]


def build_us_bonds() -> list[dict[str, Any]]:
    bonds = _load("us_bonds.json") or []
    return [dict(b) for b in bonds]


def build_fno_derivatives() -> list[dict[str, Any]]:
    fo = _load("nse_fo.json") or []
    return [
        {
            "symbol": r["symbol"],
            "name": r.get("name") or r["symbol"],
            "sub_category": "fno_underlying",
            "tags": ["NSE", "FNO"],
            "lot_size": r.get("lot_size"),
        }
        for r in fo
    ]


# ---------------------------------------------------------------------------
# Public: merge with curated CATEGORY_REGISTRY from markets_fetcher
# ---------------------------------------------------------------------------
def build_full_registry() -> dict[str, list[dict[str, Any]]]:
    """
    Returns a dict[category_id] -> list[instrument_dict].

    Categories are a superset of the curated ones in markets_fetcher.py:
      - india_equity          (all NSE equity with index tags)
      - bse_equity            (all BSE A-group)
      - india_mf              (all AMFI schemes)
      - india_fno             (all F&O underlyings)
      - crypto                (top 100 by market cap)
      - forex                 (majors + INR + emerging + crosses)
      - metals                (futures + ETFs + Indian physical)
      - real_estate           (REITs + InvITs + ETFs)
    """
    reg: dict[str, list[dict[str, Any]]] = {
        "india_equity_all": build_india_equity(),
        "bse_equity": build_bse_equity(),
        "india_mf_all": build_india_mf(),
        "india_fno": build_fno_derivatives(),
        "india_bonds_all": build_india_bonds(),
        "us_equity_all": build_us_equity(),
        "us_bonds_all": build_us_bonds(),
        "crypto_all": build_crypto(),
        "forex_all": build_forex(),
        "metals_all": build_metals(),
        "real_estate_all": build_real_estate(),
    }
    # Drop empty categories so UI doesn't show 0-count pills
    return {k: v for k, v in reg.items() if v}


def has_universe_cache() -> bool:
    """Quick check: do we have at least the NSE equity cache?"""
    return (UNIVERSE_DIR / "nse_equity.json").exists()


def category_summary() -> list[dict[str, Any]]:
    reg = build_full_registry()
    return [
        {"id": cat, "label": cat.replace("_", " ").title(), "count": len(rows)}
        for cat, rows in reg.items()
    ]


# ---------------------------------------------------------------------------
# Per-symbol tag lookup (used by curated entries in markets_fetcher)
# ---------------------------------------------------------------------------
_tag_cache: dict[str, list[str]] | None = None


def tags_for_symbol(yf_symbol: str) -> list[str]:
    """Returns the index-membership / type tags for any yfinance symbol."""
    global _tag_cache
    if _tag_cache is None:
        _tag_cache = {}
        reg = build_full_registry()
        for _, rows in reg.items():
            for r in rows:
                sym = r.get("symbol")
                if sym:
                    existing = set(_tag_cache.get(sym, []))
                    existing.update(r.get("tags") or [])
                    _tag_cache[sym] = sorted(existing)
    return _tag_cache.get(yf_symbol, [])


def invalidate_cache() -> None:
    global _tag_cache
    _tag_cache = None
