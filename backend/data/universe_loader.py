"""
Universe Loader — downloads the complete tradeable universe for every asset
class and writes JSON caches under data/universe/ that the runtime registry
loads without re-hitting network.

Sources (all free / public):
  • NSE archives       — EQUITY_L.csv (all NSE equity)
  • BSE API            — Equity.csv (fallback static list)
  • AMFI               — NAVAll.txt (all Indian mutual funds)
  • NSE indices        — ind_nifty{50,100,200,500,next50}list, midcap/smallcap/
                         microcap lists, 14 sectoral indices
  • BSE indices        — Sensex (curated static list)
  • NSE F&O            — fo_mktlots.csv
  • CoinGecko          — top 100 coins by market cap
  • NASDAQ Trader      — nasdaqlisted.txt + otherlisted.txt (ALL US equity:
                         NASDAQ + NYSE + NYSE American + NYSE Arca + BATS + IEX)
  • datahub.io         — S&P 500 constituents with GICS sector
  • Static             — Nasdaq 100, Dow 30, Russell 2000 top, S&P MidCap 400,
                         S&P SmallCap 600, forex majors + crosses, metals
                         (COMEX / NYMEX / LME / MCX / physical India), REITs,
                         InvITs, India bonds (G-Secs + SGBs + Bharat Bond +
                         liquid ETFs), US bonds (Treasuries by duration, TIPS,
                         IG corporate, HY corporate, muni, MBS, EM, floating,
                         bank loan, preferred, convertible, zero-coupon)

Each call is guarded — a failure in one source never blocks the others.
Re-run safe (overwrites JSON atomically).
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_DIR = ROOT / "data" / "universe"
UNIVERSE_DIR.mkdir(parents=True, exist_ok=True)

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _write_json(name: str, payload: Any) -> Path:
    path = UNIVERSE_DIR / name
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    os.replace(tmp, path)
    return path


def _read_json(name: str) -> Any:
    path = UNIVERSE_DIR / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _http_get(url: str, timeout: float = 20.0) -> str | None:
    try:
        with httpx.Client(
            headers=HTTP_HEADERS, timeout=timeout, follow_redirects=True
        ) as c:
            r = c.get(url)
            r.raise_for_status()
            return r.text
    except Exception as e:
        log.warning("http GET failed %s: %s", url, e)
        return None


def _nse_session() -> httpx.Client | None:
    """NSE blocks naked HTTP — must warm up a cookie first."""
    try:
        c = httpx.Client(headers=HTTP_HEADERS, timeout=20.0, follow_redirects=True)
        c.get("https://www.nseindia.com")
        return c
    except Exception as e:
        log.warning("NSE session warm-up failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# NSE full equity list
# ---------------------------------------------------------------------------
def load_nse_equity() -> list[dict[str, Any]]:
    """Fetch EQUITY_L.csv — every equity listed on NSE."""
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    txt = _http_get(url)
    if not txt:
        cached = _read_json("nse_equity.json")
        return cached or []
    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(txt))
    for r in reader:
        sym = (r.get("SYMBOL") or "").strip()
        name = (r.get("NAME OF COMPANY") or "").strip()
        series = (r.get(" SERIES") or r.get("SERIES") or "").strip()
        if not sym:
            continue
        rows.append(
            {
                "symbol": f"{sym}.NS",
                "nse_symbol": sym,
                "name": name,
                "series": series,
                "isin": (r.get(" ISIN NUMBER") or r.get("ISIN NUMBER") or "").strip(),
                "exchange": "NSE",
            }
        )
    _write_json("nse_equity.json", rows)
    log.info("NSE equity universe: %d symbols", len(rows))
    return rows


# ---------------------------------------------------------------------------
# BSE equity list (fallback static top list; BSE feed needs auth)
# ---------------------------------------------------------------------------
def load_bse_equity() -> list[dict[str, Any]]:
    """BSE public scrip master — attempts BSE API, falls back to cache."""
    url = "https://api.bseindia.com/BseIndiaAPI/api/ListOfScripData/w?Group=A&Segment=Equity&Status=Active"
    txt = _http_get(url)
    rows: list[dict[str, Any]] = []
    if txt:
        try:
            data = json.loads(txt)
            for r in data:
                sym = (r.get("SCRIP_CD") or "").strip()
                name = (r.get("SCRIP_NAME") or r.get("scrip_name") or "").strip()
                if not sym:
                    continue
                rows.append(
                    {
                        "symbol": f"{sym}.BO",
                        "bse_code": sym,
                        "name": name,
                        "isin": (r.get("ISIN_NUMBER") or "").strip(),
                        "exchange": "BSE",
                    }
                )
        except Exception as e:
            log.warning("BSE parse failed: %s", e)
    if not rows:
        cached = _read_json("bse_equity.json")
        return cached or []
    _write_json("bse_equity.json", rows)
    log.info("BSE equity universe: %d symbols", len(rows))
    return rows


# ---------------------------------------------------------------------------
# AMFI mutual funds (complete NAV list)
# ---------------------------------------------------------------------------
def load_amfi_mutual_funds() -> list[dict[str, Any]]:
    """Parse AMFI's NAVAll.txt — every MF scheme with NAV."""
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    txt = _http_get(url, timeout=40.0)
    if not txt:
        cached = _read_json("amfi_mf.json")
        return cached or []
    rows: list[dict[str, Any]] = []
    current_amc = ""
    current_type = ""
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Scheme Code"):
            continue
        # Section header lines have no semicolons
        if ";" not in line:
            # AMC or scheme-type header line
            if "Mutual Fund" in line or "Open Ended" in line or "Close Ended" in line:
                if "Mutual Fund" in line:
                    current_amc = line
                else:
                    current_type = line
            continue
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 5:
            continue
        scheme_code, isin_g, isin_div, scheme_name, nav = parts[0], parts[1], parts[2], parts[3], parts[4]
        if not scheme_code.isdigit():
            continue
        try:
            nav_f = float(nav) if nav and nav != "N.A." else None
        except ValueError:
            nav_f = None
        rows.append(
            {
                "symbol": scheme_code,  # AMFI code, not yfinance
                "amfi_code": scheme_code,
                "name": scheme_name,
                "isin_growth": isin_g,
                "isin_div": isin_div,
                "nav": nav_f,
                "amc": current_amc,
                "type": current_type,
            }
        )
    _write_json("amfi_mf.json", rows)
    log.info("AMFI MF universe: %d schemes", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Index constituents (NSE + BSE)
# ---------------------------------------------------------------------------
NSE_INDEX_FILES: dict[str, tuple[str, str]] = {
    # tag -> (niftyindices CSV path, human label)
    "NIFTY50": ("ind_nifty50list.csv", "Nifty 50"),
    "NIFTY100": ("ind_nifty100list.csv", "Nifty 100"),
    "NIFTY200": ("ind_nifty200list.csv", "Nifty 200"),
    "NIFTY500": ("ind_nifty500list.csv", "Nifty 500"),
    "NIFTYNEXT50": ("ind_niftynext50list.csv", "Nifty Next 50"),
    "NIFTYMIDCAP150": ("ind_niftymidcap150list.csv", "Nifty Midcap 150"),
    "NIFTYSMALLCAP250": ("ind_niftysmallcap250list.csv", "Nifty Smallcap 250"),
    "NIFTYMICROCAP250": ("ind_niftymicrocap250_list.csv", "Nifty Microcap 250"),
    "NIFTYBANK": ("ind_niftybanklist.csv", "Nifty Bank"),
    "NIFTYIT": ("ind_niftyitlist.csv", "Nifty IT"),
    "NIFTYAUTO": ("ind_niftyautolist.csv", "Nifty Auto"),
    "NIFTYFMCG": ("ind_niftyfmcglist.csv", "Nifty FMCG"),
    "NIFTYPHARMA": ("ind_niftypharmalist.csv", "Nifty Pharma"),
    "NIFTYMETAL": ("ind_niftymetallist.csv", "Nifty Metal"),
    "NIFTYENERGY": ("ind_niftyenergylist.csv", "Nifty Energy"),
    "NIFTYREALTY": ("ind_niftyrealtylist.csv", "Nifty Realty"),
    "NIFTYFINSERV": ("ind_niftyfinancelist.csv", "Nifty Financial Services"),
    "NIFTYMEDIA": ("ind_niftymedialist.csv", "Nifty Media"),
    "NIFTYPSUBANK": ("ind_niftypsubanklist.csv", "Nifty PSU Bank"),
    "NIFTYPVTBANK": ("ind_niftyprivatebanklist.csv", "Nifty Private Bank"),
    "NIFTYCONSUMERDUR": ("ind_niftyconsumerdurableslist.csv", "Nifty Consumer Durables"),
    "NIFTYHEALTHCARE": ("ind_niftyhealthcarelist.csv", "Nifty Healthcare"),
    "NIFTYOILANDGAS": ("ind_niftyoilandgaslist.csv", "Nifty Oil & Gas"),
}

NIFTYINDICES_BASE = "https://www.niftyindices.com/IndexConstituent/"


def _fetch_nifty_list(file_name: str) -> list[str]:
    url = f"{NIFTYINDICES_BASE}{file_name}"
    txt = _http_get(url)
    if not txt:
        return []
    symbols: list[str] = []
    reader = csv.DictReader(io.StringIO(txt))
    for r in reader:
        sym = (r.get("Symbol") or r.get("SYMBOL") or "").strip()
        if sym:
            symbols.append(sym)
    return symbols


def load_nse_index_constituents() -> dict[str, list[str]]:
    """For each index tag, the list of NSE symbols in it."""
    out: dict[str, list[str]] = {}
    for tag, (file_name, _label) in NSE_INDEX_FILES.items():
        syms = _fetch_nifty_list(file_name)
        if syms:
            out[tag] = syms
    # Cache-merge: preserve previously fetched indices if this run missed some
    cached = _read_json("nse_indices.json") or {}
    for tag, syms in cached.items():
        out.setdefault(tag, syms)
    if out:
        _write_json("nse_indices.json", out)
    log.info(
        "NSE index constituents: %d indices, %d total memberships",
        len(out),
        sum(len(v) for v in out.values()),
    )
    return out


BSE_INDEX_CONSTITUENTS: dict[str, list[str]] = {
    # Top 30 Sensex constituents (BSE codes → used as tags only)
    "SENSEX": [
        "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "HINDUNILVR",
        "ITC", "LT", "SBIN", "BHARTIARTL", "KOTAKBANK", "AXISBANK",
        "BAJFINANCE", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "NESTLEIND",
        "POWERGRID", "ULTRACEMCO", "NTPC", "HCLTECH", "TATAMOTORS", "TATASTEEL",
        "TECHM", "WIPRO", "M&M", "JSWSTEEL", "INDUSINDBK", "BAJAJFINSV",
    ],
}


def load_bse_index_constituents() -> dict[str, list[str]]:
    # BSE 100/200/500 are large-overlap with NSE lists; we rely on Sensex only
    # unless we can fetch. (BSE publishes these as Excel behind auth.)
    out = dict(BSE_INDEX_CONSTITUENTS)
    _write_json("bse_indices.json", out)
    return out


# ---------------------------------------------------------------------------
# NSE F&O
# ---------------------------------------------------------------------------
def load_nse_fo() -> list[dict[str, Any]]:
    """Fetch fo_mktlots.csv — all F&O-eligible symbols + market lots."""
    url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    txt = _http_get(url)
    if not txt:
        cached = _read_json("nse_fo.json")
        return cached or []
    rows: list[dict[str, Any]] = []
    for line in txt.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        # Skip header lines
        if parts[0].upper() in ("UNDERLYING", "SYMBOL"):
            continue
        symbol = parts[1].strip()
        name = parts[0].strip()
        if not symbol or symbol.upper() == "SYMBOL":
            continue
        # Try to get the most recent month's lot size
        lot = None
        for p in parts[2:]:
            if p.isdigit():
                lot = int(p)
                break
        rows.append(
            {
                "symbol": f"{symbol}.NS",
                "nse_symbol": symbol,
                "name": name,
                "lot_size": lot,
            }
        )
    _write_json("nse_fo.json", rows)
    log.info("NSE F&O universe: %d symbols", len(rows))
    return rows


# ---------------------------------------------------------------------------
# CoinGecko top coins
# ---------------------------------------------------------------------------
def load_coingecko_top(n: int = 100) -> list[dict[str, Any]]:
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency=usd&order=market_cap_desc&per_page={n}&page=1"
    )
    txt = _http_get(url)
    if not txt:
        cached = _read_json("crypto_top.json")
        return cached or []
    try:
        data = json.loads(txt)
    except Exception:
        return _read_json("crypto_top.json") or []
    rows: list[dict[str, Any]] = []
    for c in data:
        sym = (c.get("symbol") or "").upper()
        if not sym:
            continue
        rows.append(
            {
                "symbol": f"{sym}-USD",
                "name": c.get("name"),
                "cg_id": c.get("id"),
                "market_cap_rank": c.get("market_cap_rank"),
            }
        )
    _write_json("crypto_top.json", rows)
    log.info("CoinGecko top crypto: %d", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Static lists (forex, metals, REITs) — reliable yfinance symbols
# ---------------------------------------------------------------------------
FOREX_PAIRS = [
    # Majors
    ("EURUSD=X", "EUR/USD", "major"),
    ("GBPUSD=X", "GBP/USD", "major"),
    ("USDJPY=X", "USD/JPY", "major"),
    ("USDCHF=X", "USD/CHF", "major"),
    ("AUDUSD=X", "AUD/USD", "major"),
    ("NZDUSD=X", "NZD/USD", "major"),
    ("USDCAD=X", "USD/CAD", "major"),
    # INR crosses
    ("USDINR=X", "USD/INR", "inr_cross"),
    ("EURINR=X", "EUR/INR", "inr_cross"),
    ("GBPINR=X", "GBP/INR", "inr_cross"),
    ("JPYINR=X", "JPY/INR", "inr_cross"),
    ("AUDINR=X", "AUD/INR", "inr_cross"),
    ("CADINR=X", "CAD/INR", "inr_cross"),
    ("CHFINR=X", "CHF/INR", "inr_cross"),
    ("SGDINR=X", "SGD/INR", "inr_cross"),
    ("CNYINR=X", "CNY/INR", "inr_cross"),
    ("AEDINR=X", "AED/INR", "inr_cross"),
    # Emerging / Asia
    ("USDCNY=X", "USD/CNY", "emerging"),
    ("USDSGD=X", "USD/SGD", "emerging"),
    ("USDHKD=X", "USD/HKD", "emerging"),
    ("USDKRW=X", "USD/KRW", "emerging"),
    ("USDTHB=X", "USD/THB", "emerging"),
    ("USDMYR=X", "USD/MYR", "emerging"),
    ("USDIDR=X", "USD/IDR", "emerging"),
    ("USDTWD=X", "USD/TWD", "emerging"),
    ("USDPHP=X", "USD/PHP", "emerging"),
    ("USDMXN=X", "USD/MXN", "emerging"),
    ("USDBRL=X", "USD/BRL", "emerging"),
    ("USDZAR=X", "USD/ZAR", "emerging"),
    ("USDTRY=X", "USD/TRY", "emerging"),
    # Crosses
    ("EURGBP=X", "EUR/GBP", "cross"),
    ("EURJPY=X", "EUR/JPY", "cross"),
    ("GBPJPY=X", "GBP/JPY", "cross"),
    ("EURCHF=X", "EUR/CHF", "cross"),
    ("AUDJPY=X", "AUD/JPY", "cross"),
    # Indexes
    ("DX-Y.NYB", "US Dollar Index (DXY)", "index"),
]

METALS_GLOBAL = [
    # Precious
    ("GC=F", "Gold Futures", "precious_metal", ["COMEX"]),
    ("SI=F", "Silver Futures", "precious_metal", ["COMEX"]),
    ("PL=F", "Platinum Futures", "precious_metal", ["NYMEX"]),
    ("PA=F", "Palladium Futures", "precious_metal", ["NYMEX"]),
    ("MGC=F", "Micro Gold", "precious_metal", ["COMEX"]),
    ("SIL=F", "Micro Silver", "precious_metal", ["COMEX"]),
    # Base
    ("HG=F", "Copper Futures", "base_metal", ["COMEX"]),
    ("ALI=F", "Aluminum Futures", "base_metal", ["LME"]),
    ("ZN=F", "Zinc (proxy/10Y note)", "base_metal", []),
    ("NI=F", "Nickel Futures", "base_metal", ["LME"]),
    # Gold ETFs
    ("GLD", "SPDR Gold Shares", "precious_etf", ["ETF"]),
    ("IAU", "iShares Gold Trust", "precious_etf", ["ETF"]),
    ("SLV", "iShares Silver Trust", "precious_etf", ["ETF"]),
    ("PPLT", "Aberdeen Platinum ETF", "precious_etf", ["ETF"]),
    ("PALL", "Aberdeen Palladium ETF", "precious_etf", ["ETF"]),
    # Indian gold ETFs
    ("GOLDBEES.NS", "Nippon India Gold ETF", "india_gold_etf", ["NSE"]),
    ("GOLDSHARE.NS", "UTI Gold ETF", "india_gold_etf", ["NSE"]),
    ("HDFCGOLD.NS", "HDFC Gold ETF", "india_gold_etf", ["NSE"]),
    ("KOTAKGOLD.NS", "Kotak Gold ETF", "india_gold_etf", ["NSE"]),
    ("SILVERBEES.NS", "Nippon Silver ETF", "india_silver_etf", ["NSE"]),
]

# India physical metal purities + types synthesized from spot + premium
INDIA_PHYSICAL_METALS = [
    {"symbol": "GOLD-24K-IN", "name": "Gold 24K (999)", "sub_category": "physical_gold", "purity": "24K", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "GOLD-22K-IN", "name": "Gold 22K (916)", "sub_category": "physical_gold", "purity": "22K", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "GOLD-18K-IN", "name": "Gold 18K (750)", "sub_category": "physical_gold", "purity": "18K", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "GOLD-14K-IN", "name": "Gold 14K (585)", "sub_category": "physical_gold", "purity": "14K", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "SILVER-999-IN", "name": "Silver 999 (Fine)", "sub_category": "physical_silver", "purity": "999", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "SILVER-925-IN", "name": "Silver 925 (Sterling)", "sub_category": "physical_silver", "purity": "925", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "PLATINUM-950-IN", "name": "Platinum 950", "sub_category": "physical_platinum", "purity": "950", "tags": ["PHYSICAL", "INDIA"]},
    {"symbol": "COPPER-IN", "name": "Copper (MCX spot)", "sub_category": "physical_copper", "purity": "spot", "tags": ["PHYSICAL", "INDIA", "MCX"]},
]

REITS_INVITS = [
    # India REITs
    ("EMBASSY.NS", "Embassy Office Parks REIT", "india_reit", ["NSE", "REIT"]),
    ("MINDSPACE.NS", "Mindspace Business Parks REIT", "india_reit", ["NSE", "REIT"]),
    ("BIRET.NS", "Brookfield India REIT", "india_reit", ["NSE", "REIT"]),
    ("NAMREIT.NS", "Nexus Select Trust REIT", "india_reit", ["NSE", "REIT"]),
    # India InvITs
    ("IRBINVIT.NS", "IRB InvIT Fund", "india_invit", ["NSE", "INVIT"]),
    ("INDIGRID.NS", "India Grid Trust", "india_invit", ["NSE", "INVIT"]),
    ("POWERINDIA.NS", "Power Grid InvIT", "india_invit", ["NSE", "INVIT"]),
    # US REITs
    ("VNQ", "Vanguard Real Estate ETF", "us_reit_etf", ["NYSE", "ETF"]),
    ("IYR", "iShares US Real Estate ETF", "us_reit_etf", ["NYSE", "ETF"]),
    ("XLRE", "Real Estate Select Sector SPDR", "us_reit_etf", ["NYSE", "ETF"]),
    ("O", "Realty Income", "us_reit", ["NYSE", "REIT"]),
    ("AMT", "American Tower", "us_reit", ["NYSE", "REIT"]),
    ("PLD", "Prologis", "us_reit", ["NYSE", "REIT"]),
    ("SPG", "Simon Property Group", "us_reit", ["NYSE", "REIT"]),
    ("EQIX", "Equinix", "us_reit", ["NYSE", "REIT"]),
    ("CCI", "Crown Castle", "us_reit", ["NYSE", "REIT"]),
    ("DLR", "Digital Realty", "us_reit", ["NYSE", "REIT"]),
    ("PSA", "Public Storage", "us_reit", ["NYSE", "REIT"]),
    ("WELL", "Welltower", "us_reit", ["NYSE", "REIT"]),
    ("AVB", "AvalonBay Communities", "us_reit", ["NYSE", "REIT"]),
    ("EXR", "Extra Space Storage", "us_reit", ["NYSE", "REIT"]),
]


def load_static_lists() -> None:
    _write_json("forex.json", [
        {"symbol": s, "name": n, "sub_category": sub, "tags": ["FOREX"]}
        for s, n, sub in FOREX_PAIRS
    ])
    _write_json("metals.json", [
        {"symbol": s, "name": n, "sub_category": sub, "tags": tags}
        for s, n, sub, tags in METALS_GLOBAL
    ])
    _write_json("metals_india_physical.json", INDIA_PHYSICAL_METALS)
    _write_json("reits_invits.json", [
        {"symbol": s, "name": n, "sub_category": sub, "tags": tags}
        for s, n, sub, tags in REITS_INVITS
    ])


# ---------------------------------------------------------------------------
# US equity universe — NASDAQ Trader public files
# ---------------------------------------------------------------------------
# nasdaqlisted.txt  = all NASDAQ-listed securities
# otherlisted.txt   = all NYSE, AMEX, BATS, ARCA listed securities
# Both are pipe-delimited, authoritative, and updated daily.
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"


def _parse_pipe_table(txt: str) -> list[dict[str, str]]:
    """Parse nasdaqtrader's pipe-delimited files (last row is a checksum)."""
    rows: list[dict[str, str]] = []
    lines = [line for line in txt.splitlines() if line.strip()]
    if not lines:
        return rows
    header = lines[0].split("|")
    for line in lines[1:]:
        if line.startswith("File Creation Time"):
            continue
        parts = line.split("|")
        if len(parts) != len(header):
            continue
        rows.append(dict(zip(header, parts)))
    return rows


def _exchange_label(code: str) -> str:
    return {
        "N": "NYSE",
        "A": "NYSE_AMERICAN",
        "P": "NYSE_ARCA",
        "Z": "CBOE_BZX",
        "V": "IEX",
    }.get(code, code or "")


def load_us_equity() -> list[dict[str, Any]]:
    """Full US equity universe from NASDAQ Trader (NASDAQ + NYSE + AMEX)."""
    rows: list[dict[str, Any]] = []

    # NASDAQ-listed
    txt = _http_get(NASDAQ_LISTED_URL, timeout=30.0)
    if txt:
        for r in _parse_pipe_table(txt):
            sym = (r.get("Symbol") or "").strip()
            if not sym:
                continue
            # skip test issues
            if (r.get("Test Issue") or "N") == "Y":
                continue
            name = (r.get("Security Name") or "").strip()
            etf = (r.get("ETF") or "N") == "Y"
            rows.append(
                {
                    "symbol": sym,
                    "name": name,
                    "exchange": "NASDAQ",
                    "market_category": (r.get("Market Category") or "").strip(),
                    "is_etf": etf,
                    "is_us_listed": True,
                }
            )

    # Other-listed (NYSE, NYSE American, NYSE Arca, BATS, IEX)
    txt = _http_get(OTHER_LISTED_URL, timeout=30.0)
    if txt:
        for r in _parse_pipe_table(txt):
            sym = (r.get("ACT Symbol") or r.get("NASDAQ Symbol") or "").strip()
            if not sym:
                continue
            if (r.get("Test Issue") or "N") == "Y":
                continue
            name = (r.get("Security Name") or "").strip()
            etf = (r.get("ETF") or "N") == "Y"
            rows.append(
                {
                    "symbol": sym,
                    "name": name,
                    "exchange": _exchange_label(r.get("Exchange") or ""),
                    "is_etf": etf,
                    "is_us_listed": True,
                }
            )

    if not rows:
        cached = _read_json("us_equity.json")
        return cached or []

    # Dedup by symbol — NASDAQ sometimes echoes the same symbol on ARCA
    seen: dict[str, dict[str, Any]] = {}
    for r in rows:
        seen.setdefault(r["symbol"], r)
    deduped = list(seen.values())
    _write_json("us_equity.json", deduped)
    log.info("US equity universe: %d symbols", len(deduped))
    return deduped


# ---------------------------------------------------------------------------
# US index constituents
# ---------------------------------------------------------------------------
# S&P 500 via datahub.io mirror (public, well-maintained)
SP500_CSV = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"


def load_sp500() -> list[dict[str, Any]]:
    """S&P 500 constituents with GICS sector tag."""
    txt = _http_get(SP500_CSV)
    if not txt:
        cached = _read_json("sp500.json")
        return cached or []
    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(txt))
    for r in reader:
        sym = (r.get("Symbol") or "").strip()
        if not sym:
            continue
        rows.append(
            {
                "symbol": sym.replace(".", "-"),  # yfinance uses BRK-B not BRK.B
                "name": (r.get("Security") or r.get("Name") or "").strip(),
                "sector": (r.get("GICS Sector") or r.get("Sector") or "").strip(),
                "sub_industry": (r.get("GICS Sub-Industry") or "").strip(),
            }
        )
    if rows:
        _write_json("sp500.json", rows)
        log.info("S&P 500 constituents: %d", len(rows))
    return rows


# Nasdaq 100 — static as these rarely change; top ~100 by market cap
NASDAQ100 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "AVGO", "TSLA",
    "COST", "NFLX", "TMUS", "ADBE", "AMD", "PEP", "LIN", "CSCO", "QCOM",
    "INTU", "TXN", "AMGN", "ISRG", "CMCSA", "AMAT", "HON", "PANW", "VRTX",
    "BKNG", "SBUX", "ADP", "GILD", "ADI", "MU", "MDLZ", "LRCX", "REGN",
    "KLAC", "SNPS", "CDNS", "MELI", "CRWD", "MAR", "PYPL", "CTAS", "ORLY",
    "CEG", "CSX", "PDD", "ABNB", "NXPI", "WDAY", "FTNT", "ASML", "ROP",
    "CHTR", "ADSK", "DASH", "MNST", "AEP", "KDP", "PAYX", "ODFL", "FANG",
    "PCAR", "TEAM", "ROST", "LULU", "CPRT", "IDXX", "FAST", "EXC", "MRVL",
    "XEL", "VRSK", "CTSH", "TTD", "KHC", "DDOG", "DXCM", "EA", "CSGP",
    "GEHC", "ANSS", "BKR", "CCEP", "BIIB", "ON", "ZS", "CDW", "ILMN",
    "MDB", "WBD", "MRNA", "TTWO", "WBA", "GFS", "SIRI", "SMCI", "ARM",
    "APP",
]

# Dow 30 — rarely changes (last change 2024)
DOW30 = [
    "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS",
    "DOW", "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM",
    "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ",
    "WMT",
]

# S&P MidCap 400 + SmallCap 600 top constituents (representative subsets)
# Full lists require paid data; static subsets preserve index tags without
# adding fragile network dependencies.
SP_MIDCAP400_TOP = [
    "SPG", "TRGP", "WSM", "BURL", "CASY", "EQH", "DECK", "FIX", "TOL", "LECO",
    "RPM", "WING", "MANH", "JEF", "PSTG", "CHDN", "CLH", "FNF", "USFD", "EME",
]
SP_SMALLCAP600_TOP = [
    "MLI", "FIX", "BMI", "SFM", "GKOS", "ESNT", "EXLS", "CRS", "ENSG", "AWI",
]

# Russell 2000 top names (static subset — full list from IWB holdings requires
# auth; the top 100 covers the most-traded names)
RUSSELL2000_TOP = [
    "SMCI", "SMTC", "FTAI", "CARG", "CRS", "ENSG", "AWI", "AMR", "BMI",
    "MLI", "KTB", "EXLS", "PJT", "LPX", "CRVL", "MMSI", "BRBR", "RGA",
    "SFM", "FNB", "GTLS", "WMS", "GMS", "PINC", "OHI", "RHP",
]


def _save_us_indices() -> dict[str, list[str]]:
    sp500 = [r["symbol"] for r in load_sp500()]
    out = {
        "SP500": sp500,
        "NASDAQ100": NASDAQ100,
        "DOW30": DOW30,
        "SP_MIDCAP400": SP_MIDCAP400_TOP,
        "SP_SMALLCAP600": SP_SMALLCAP600_TOP,
        "RUSSELL2000": RUSSELL2000_TOP,
    }
    # keep existing cached tags if a run misses S&P
    cached = _read_json("us_indices.json") or {}
    for tag, syms in cached.items():
        out.setdefault(tag, syms)
    _write_json("us_indices.json", out)
    return out


# S&P 500 sector → tag map (GICS)
GICS_SECTOR_TAGS = {
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


# ---------------------------------------------------------------------------
# Bonds — India & USA (curated, broad-coverage static list)
# ---------------------------------------------------------------------------
# Individual bond CUSIPs/ISINs need paid feeds; for retail + lab use, tradeable
# ETFs + benchmark yields give the best coverage.

INDIA_BONDS = [
    # Govt yields (yfinance carries India 10Y as ^IRX proxy? No — use FRED)
    {"symbol": "INDIA10YT=RR", "name": "India 10Y G-Sec Yield", "sub_category": "govt_yield", "tags": ["INDIA", "GSEC", "YIELD"]},
    {"symbol": "INDIA5YT=RR", "name": "India 5Y G-Sec Yield", "sub_category": "govt_yield", "tags": ["INDIA", "GSEC", "YIELD"]},
    {"symbol": "INDIA2YT=RR", "name": "India 2Y G-Sec Yield", "sub_category": "govt_yield", "tags": ["INDIA", "GSEC", "YIELD"]},
    {"symbol": "INDIA30YT=RR", "name": "India 30Y G-Sec Yield", "sub_category": "govt_yield", "tags": ["INDIA", "GSEC", "YIELD"]},
    # Liquid / Overnight ETFs
    {"symbol": "LIQUIDBEES.NS", "name": "Nippon India Liquid BeES ETF", "sub_category": "liquid_etf", "tags": ["NSE", "BOND_ETF", "LIQUID"]},
    {"symbol": "LIQUID.NS", "name": "ICICI Pru Liquid ETF", "sub_category": "liquid_etf", "tags": ["NSE", "BOND_ETF", "LIQUID"]},
    {"symbol": "LIQUIDCASE.NS", "name": "Axis AMC Liquid ETF", "sub_category": "liquid_etf", "tags": ["NSE", "BOND_ETF", "LIQUID"]},
    # Govt Bond ETFs (G-Sec)
    {"symbol": "GSEC10IETF.NS", "name": "Motilal Oswal 10Y G-Sec ETF", "sub_category": "govt_etf", "tags": ["NSE", "BOND_ETF", "GSEC"]},
    {"symbol": "BBETF0431.NS", "name": "Bharat Bond ETF April 2031", "sub_category": "govt_etf", "tags": ["NSE", "BOND_ETF", "GSEC", "TARGET_MATURITY"]},
    {"symbol": "BBETF0432.NS", "name": "Bharat Bond ETF April 2032", "sub_category": "govt_etf", "tags": ["NSE", "BOND_ETF", "GSEC", "TARGET_MATURITY"]},
    {"symbol": "BBETF0433.NS", "name": "Bharat Bond ETF April 2033", "sub_category": "govt_etf", "tags": ["NSE", "BOND_ETF", "GSEC", "TARGET_MATURITY"]},
    # PSU / Corporate
    {"symbol": "CPSEETF.NS", "name": "CPSE ETF", "sub_category": "psu_etf", "tags": ["NSE", "BOND_ETF", "PSU"]},
    {"symbol": "BHARAT22.NS", "name": "Bharat 22 ETF", "sub_category": "psu_etf", "tags": ["NSE", "BOND_ETF", "PSU"]},
    # SDL / State Development Loans
    {"symbol": "SDL24.NS", "name": "Nippon India ETF Nifty SDL", "sub_category": "state_loan", "tags": ["NSE", "BOND_ETF", "SDL"]},
    # Sovereign Gold Bonds (SGB) — gold-linked govt bonds
    {"symbol": "SGBAUG28.BO", "name": "Sovereign Gold Bond Aug 2028", "sub_category": "sgb", "tags": ["BSE", "SGB", "GOLD_BOND"]},
    {"symbol": "SGBJUL30.BO", "name": "Sovereign Gold Bond Jul 2030", "sub_category": "sgb", "tags": ["BSE", "SGB", "GOLD_BOND"]},
    {"symbol": "SGBNOV31.BO", "name": "Sovereign Gold Bond Nov 2031", "sub_category": "sgb", "tags": ["BSE", "SGB", "GOLD_BOND"]},
    # Corporate / NCD ETFs
    {"symbol": "NETFCORPB.NS", "name": "Nippon India ETF Nifty CPSE Bond", "sub_category": "corporate_etf", "tags": ["NSE", "BOND_ETF", "CORPORATE"]},
    {"symbol": "LTGILTBEES.NS", "name": "Long Term Gilt BeES", "sub_category": "govt_etf", "tags": ["NSE", "BOND_ETF", "GSEC"]},
]

US_BONDS_FULL = [
    # Treasury yield benchmarks
    {"symbol": "^IRX", "name": "US 13-Week T-Bill", "sub_category": "tbill_yield", "tags": ["USA", "TREASURY", "YIELD"]},
    {"symbol": "^FVX", "name": "US 5Y Treasury Yield", "sub_category": "treasury_yield", "tags": ["USA", "TREASURY", "YIELD"]},
    {"symbol": "^TNX", "name": "US 10Y Treasury Yield", "sub_category": "treasury_yield", "tags": ["USA", "TREASURY", "YIELD"]},
    {"symbol": "^TYX", "name": "US 30Y Treasury Yield", "sub_category": "treasury_yield", "tags": ["USA", "TREASURY", "YIELD"]},
    # Treasury ETFs by duration
    {"symbol": "BIL", "name": "SPDR 1-3 Month T-Bill ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "SHORT"]},
    {"symbol": "SHV", "name": "iShares Short Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "SHORT"]},
    {"symbol": "SHY", "name": "iShares 1-3Y Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "SHORT"]},
    {"symbol": "VGSH", "name": "Vanguard Short Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "SHORT"]},
    {"symbol": "IEI", "name": "iShares 3-7Y Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "INTERMEDIATE"]},
    {"symbol": "IEF", "name": "iShares 7-10Y Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "INTERMEDIATE"]},
    {"symbol": "VGIT", "name": "Vanguard Intermediate Treasury", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "INTERMEDIATE"]},
    {"symbol": "TLH", "name": "iShares 10-20Y Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "LONG"]},
    {"symbol": "TLT", "name": "iShares 20+Y Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "LONG"]},
    {"symbol": "VGLT", "name": "Vanguard Long Treasury ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "LONG"]},
    {"symbol": "GOVT", "name": "iShares US Treasury Bond ETF", "sub_category": "treasury_etf", "tags": ["NYSE", "BOND_ETF", "TREASURY", "BROAD"]},
    # TIPS — inflation protected
    {"symbol": "TIP", "name": "iShares TIPS Bond ETF", "sub_category": "tips", "tags": ["NYSE", "BOND_ETF", "TIPS", "INFLATION"]},
    {"symbol": "VTIP", "name": "Vanguard Short TIPS ETF", "sub_category": "tips", "tags": ["NYSE", "BOND_ETF", "TIPS", "INFLATION", "SHORT"]},
    {"symbol": "SCHP", "name": "Schwab US TIPS ETF", "sub_category": "tips", "tags": ["NYSE", "BOND_ETF", "TIPS", "INFLATION"]},
    {"symbol": "STIP", "name": "iShares 0-5Y TIPS ETF", "sub_category": "tips", "tags": ["NYSE", "BOND_ETF", "TIPS", "INFLATION", "SHORT"]},
    # Investment grade corporate
    {"symbol": "LQD", "name": "iShares IG Corporate Bond ETF", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG"]},
    {"symbol": "VCIT", "name": "Vanguard Intermediate Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG"]},
    {"symbol": "VCSH", "name": "Vanguard Short Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG", "SHORT"]},
    {"symbol": "VCLT", "name": "Vanguard Long Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG", "LONG"]},
    {"symbol": "IGSB", "name": "iShares 1-5Y IG Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG", "SHORT"]},
    {"symbol": "IGIB", "name": "iShares 5-10Y IG Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG"]},
    {"symbol": "USIG", "name": "iShares Broad USD IG Corporate", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "IG"]},
    # High yield
    {"symbol": "HYG", "name": "iShares High Yield Corporate", "sub_category": "high_yield", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "HY"]},
    {"symbol": "JNK", "name": "SPDR High Yield Bond ETF", "sub_category": "high_yield", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "HY"]},
    {"symbol": "SHYG", "name": "iShares Short HY Corporate", "sub_category": "high_yield", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "HY", "SHORT"]},
    {"symbol": "USHY", "name": "iShares Broad USD HY Corporate", "sub_category": "high_yield", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "HY"]},
    {"symbol": "HYLB", "name": "Xtrackers USD HY Corporate", "sub_category": "high_yield", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "HY"]},
    # Broad market bond ETFs
    {"symbol": "AGG", "name": "iShares Core US Aggregate Bond", "sub_category": "aggregate", "tags": ["NYSE", "BOND_ETF", "AGGREGATE"]},
    {"symbol": "BND", "name": "Vanguard Total Bond Market", "sub_category": "aggregate", "tags": ["NYSE", "BOND_ETF", "AGGREGATE"]},
    {"symbol": "BNDX", "name": "Vanguard Total Intl Bond", "sub_category": "international", "tags": ["NYSE", "BOND_ETF", "INTERNATIONAL"]},
    {"symbol": "IUSB", "name": "iShares Core Total USD Bond", "sub_category": "aggregate", "tags": ["NYSE", "BOND_ETF", "AGGREGATE"]},
    {"symbol": "SCHZ", "name": "Schwab US Aggregate Bond", "sub_category": "aggregate", "tags": ["NYSE", "BOND_ETF", "AGGREGATE"]},
    # Municipal
    {"symbol": "MUB", "name": "iShares National Muni Bond", "sub_category": "municipal", "tags": ["NYSE", "BOND_ETF", "MUNI", "TAX_EXEMPT"]},
    {"symbol": "TFI", "name": "SPDR Nuveen Muni Bond", "sub_category": "municipal", "tags": ["NYSE", "BOND_ETF", "MUNI", "TAX_EXEMPT"]},
    {"symbol": "VTEB", "name": "Vanguard Tax-Exempt Bond", "sub_category": "municipal", "tags": ["NYSE", "BOND_ETF", "MUNI", "TAX_EXEMPT"]},
    {"symbol": "SHM", "name": "SPDR Short Muni Bond", "sub_category": "municipal", "tags": ["NYSE", "BOND_ETF", "MUNI", "SHORT"]},
    {"symbol": "HYD", "name": "VanEck HY Muni ETF", "sub_category": "municipal", "tags": ["NYSE", "BOND_ETF", "MUNI", "HY"]},
    # Mortgage-backed
    {"symbol": "MBB", "name": "iShares MBS ETF", "sub_category": "mbs", "tags": ["NYSE", "BOND_ETF", "MBS"]},
    {"symbol": "VMBS", "name": "Vanguard Mortgage-Backed", "sub_category": "mbs", "tags": ["NYSE", "BOND_ETF", "MBS"]},
    # Emerging markets
    {"symbol": "EMB", "name": "iShares JP Morgan EM Bond", "sub_category": "emerging", "tags": ["NYSE", "BOND_ETF", "EM"]},
    {"symbol": "EMLC", "name": "VanEck EM Local Currency", "sub_category": "emerging", "tags": ["NYSE", "BOND_ETF", "EM", "LOCAL"]},
    {"symbol": "PCY", "name": "Invesco EM Sovereign Debt", "sub_category": "emerging", "tags": ["NYSE", "BOND_ETF", "EM"]},
    {"symbol": "VWOB", "name": "Vanguard EM Govt Bond", "sub_category": "emerging", "tags": ["NYSE", "BOND_ETF", "EM"]},
    # Floating rate / Bank loan
    {"symbol": "FLOT", "name": "iShares Floating Rate Bond", "sub_category": "floating", "tags": ["NYSE", "BOND_ETF", "FLOATING"]},
    {"symbol": "USFR", "name": "WisdomTree Floating Treasury", "sub_category": "floating", "tags": ["NYSE", "BOND_ETF", "TREASURY", "FLOATING"]},
    {"symbol": "BKLN", "name": "Invesco Senior Loan ETF", "sub_category": "bank_loan", "tags": ["NYSE", "BOND_ETF", "BANK_LOAN"]},
    {"symbol": "SRLN", "name": "SPDR Blackstone Senior Loan", "sub_category": "bank_loan", "tags": ["NYSE", "BOND_ETF", "BANK_LOAN"]},
    # Preferred / Convertible
    {"symbol": "PFF", "name": "iShares Preferred Stock ETF", "sub_category": "preferred", "tags": ["NYSE", "BOND_ETF", "PREFERRED"]},
    {"symbol": "PGX", "name": "Invesco Preferred ETF", "sub_category": "preferred", "tags": ["NYSE", "BOND_ETF", "PREFERRED"]},
    {"symbol": "CWB", "name": "SPDR Convertible Securities", "sub_category": "convertible", "tags": ["NYSE", "BOND_ETF", "CONVERTIBLE"]},
    {"symbol": "ICVT", "name": "iShares Convertible Bond", "sub_category": "convertible", "tags": ["NYSE", "BOND_ETF", "CONVERTIBLE"]},
    # Credit (Investment-grade + HY combo)
    {"symbol": "SPAB", "name": "SPDR Aggregate Bond ETF", "sub_category": "aggregate", "tags": ["NYSE", "BOND_ETF", "AGGREGATE"]},
    {"symbol": "SPSB", "name": "SPDR Short Corporate Bond", "sub_category": "corporate_ig", "tags": ["NYSE", "BOND_ETF", "CORPORATE", "SHORT"]},
    # Active bond funds (popular)
    {"symbol": "TOTL", "name": "SPDR DoubleLine Total Return", "sub_category": "active", "tags": ["NYSE", "BOND_ETF", "ACTIVE"]},
    {"symbol": "PIMCO:PONAX", "name": "PIMCO Income Fund (proxy)", "sub_category": "active", "tags": ["MF", "ACTIVE"]},
    # Treasury STRIPS / Zero-coupon
    {"symbol": "ZROZ", "name": "PIMCO 25+Y Zero Treasury", "sub_category": "zero_coupon", "tags": ["NYSE", "BOND_ETF", "TREASURY", "ZERO", "LONG"]},
    {"symbol": "EDV", "name": "Vanguard Ext Duration Treasury", "sub_category": "zero_coupon", "tags": ["NYSE", "BOND_ETF", "TREASURY", "ZERO", "LONG"]},
]


def load_bonds_static() -> None:
    _write_json("india_bonds.json", INDIA_BONDS)
    _write_json("us_bonds.json", US_BONDS_FULL)
    log.info(
        "Bonds static: India=%d, US=%d", len(INDIA_BONDS), len(US_BONDS_FULL)
    )


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------
_progress: dict[str, Any] = {"running": False, "step": "idle", "counts": {}}


def get_progress() -> dict[str, Any]:
    return dict(_progress)


def refresh_all(fast: bool = False) -> dict[str, Any]:
    """
    Fetch every universe source. Returns counts per source.
    If fast=True, skips the full AMFI/NSE equity downloads (keeps cached).
    """
    _progress.update({"running": True, "step": "starting", "counts": {}})
    counts: dict[str, int] = {}
    try:
        _progress["step"] = "nse_equity"
        counts["nse_equity"] = len(load_nse_equity()) if not fast else len(_read_json("nse_equity.json") or [])

        _progress["step"] = "bse_equity"
        counts["bse_equity"] = len(load_bse_equity()) if not fast else len(_read_json("bse_equity.json") or [])

        _progress["step"] = "amfi_mf"
        counts["amfi_mf"] = len(load_amfi_mutual_funds()) if not fast else len(_read_json("amfi_mf.json") or [])

        _progress["step"] = "nse_indices"
        nse_idx = load_nse_index_constituents()
        counts["nse_indices"] = len(nse_idx)
        counts["nse_index_memberships"] = sum(len(v) for v in nse_idx.values())

        _progress["step"] = "bse_indices"
        bse_idx = load_bse_index_constituents()
        counts["bse_indices"] = len(bse_idx)

        _progress["step"] = "nse_fo"
        counts["nse_fo"] = len(load_nse_fo())

        _progress["step"] = "crypto"
        counts["crypto"] = len(load_coingecko_top(100))

        _progress["step"] = "us_equity"
        counts["us_equity"] = len(load_us_equity()) if not fast else len(_read_json("us_equity.json") or [])

        _progress["step"] = "us_indices"
        us_idx = _save_us_indices()
        counts["us_indices"] = len(us_idx)
        counts["us_index_memberships"] = sum(len(v) for v in us_idx.values())

        _progress["step"] = "static_lists"
        load_static_lists()
        counts["forex"] = len(FOREX_PAIRS)
        counts["metals_global"] = len(METALS_GLOBAL)
        counts["metals_india_physical"] = len(INDIA_PHYSICAL_METALS)
        counts["reits_invits"] = len(REITS_INVITS)

        _progress["step"] = "bonds"
        load_bonds_static()
        counts["india_bonds"] = len(INDIA_BONDS)
        counts["us_bonds"] = len(US_BONDS_FULL)

        _progress.update({"step": "done", "counts": counts})
    except Exception as e:
        log.exception("universe refresh failed")
        _progress["error"] = str(e)
    finally:
        _progress["running"] = False
    return counts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(json.dumps(refresh_all(), indent=2))
