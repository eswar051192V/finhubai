"""
Universal markets fetcher — pulls live data for every asset class via yfinance
plus supplementary free APIs. All prices returned in native currency with ISO code.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
import yfinance as yf

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ticker universes — kept as data so the UI can enumerate categories.
# Each entry: (yfinance symbol, human label, sub_category)
# ---------------------------------------------------------------------------

INDIA_EQUITY_MAJOR: list[tuple[str, str, str]] = [
    ("RELIANCE.NS", "Reliance Industries", "large_cap"),
    ("TCS.NS", "TCS", "large_cap"),
    ("HDFCBANK.NS", "HDFC Bank", "large_cap"),
    ("INFY.NS", "Infosys", "large_cap"),
    ("ICICIBANK.NS", "ICICI Bank", "large_cap"),
    ("HINDUNILVR.NS", "Hindustan Unilever", "large_cap"),
    ("ITC.NS", "ITC", "large_cap"),
    ("SBIN.NS", "State Bank of India", "large_cap"),
    ("BHARTIARTL.NS", "Bharti Airtel", "large_cap"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank", "large_cap"),
    ("LT.NS", "Larsen & Toubro", "large_cap"),
    ("AXISBANK.NS", "Axis Bank", "large_cap"),
    ("BAJFINANCE.NS", "Bajaj Finance", "large_cap"),
    ("MARUTI.NS", "Maruti Suzuki", "large_cap"),
    ("TATAMOTORS.NS", "Tata Motors", "large_cap"),
    ("SUNPHARMA.NS", "Sun Pharma", "large_cap"),
    ("TITAN.NS", "Titan Company", "large_cap"),
    ("ONGC.NS", "ONGC", "large_cap"),
    ("NTPC.NS", "NTPC", "large_cap"),
    ("ADANIENT.NS", "Adani Enterprises", "large_cap"),
    ("WIPRO.NS", "Wipro", "large_cap"),
    ("POWERGRID.NS", "Power Grid Corp", "large_cap"),
    ("TATASTEEL.NS", "Tata Steel", "large_cap"),
    ("ASIANPAINT.NS", "Asian Paints", "large_cap"),
    ("JSWSTEEL.NS", "JSW Steel", "large_cap"),
]

INDIA_MUTUAL_FUNDS: list[tuple[str, str, str]] = [
    ("0P0000XVAA.BO", "HDFC Flexi Cap Fund", "flexi_cap"),
    ("0P0000XVAB.BO", "ICICI Pru Bluechip Fund", "large_cap"),
    ("0P0000XVS5.BO", "SBI Small Cap Fund", "small_cap"),
    ("0P0000XVUH.BO", "Axis Long Term Equity (ELSS)", "elss"),
    ("0P0000XVS7.BO", "Mirae Asset Large Cap", "large_cap"),
    ("0P0001BAR2.BO", "Parag Parikh Flexi Cap", "flexi_cap"),
    ("0P00009WDA.BO", "Kotak Standard Multicap", "multi_cap"),
    ("0P0000XVSE.BO", "Nippon India Small Cap", "small_cap"),
]

INDIA_BONDS_ETFS: list[tuple[str, str, str]] = [
    ("LIQUIDBEES.NS", "Nippon Liquid ETF", "liquid"),
    ("LONGTERMBOND.NS", "Edelweiss NBFC Debt ETF", "corporate"),
    ("CPSEETF.NS", "CPSE ETF", "govt_psu"),
    ("BHARAT22.NS", "Bharat 22 ETF", "govt_psu"),
]

INDIA_INDEX_FUTURES: list[tuple[str, str, str]] = [
    ("^NSEI", "NIFTY 50", "index"),
    ("^NSEBANK", "Bank NIFTY", "index"),
    ("^BSESN", "SENSEX", "index"),
]

# --- Global Energy ---
ENERGY: list[tuple[str, str, str]] = [
    ("CL=F", "WTI Crude Oil", "crude"),
    ("BZ=F", "Brent Crude Oil", "crude"),
    ("NG=F", "Natural Gas (Henry Hub)", "natural_gas"),
    ("HO=F", "Heating Oil", "heating_oil"),
    ("RB=F", "RBOB Gasoline", "gasoline"),
    ("MCL=F", "Micro WTI Crude", "crude"),
    ("QG=F", "E-mini Natural Gas", "natural_gas"),
    ("LNGc1", "LNG Spot Proxy", "lng"),
    ("^GSPC", "S&P 500 (energy ref)", "index"),
    ("XLE", "Energy Select SPDR", "etf"),
    ("XOP", "S&P Oil & Gas Exploration ETF", "etf"),
    ("USO", "US Oil Fund", "etf"),
    ("UNG", "US Natural Gas Fund", "etf"),
    ("BOIL", "ProShares Ultra Bloomberg NG", "etf"),
]

# --- Commodities ---
COMMODITIES: list[tuple[str, str, str]] = [
    ("GC=F", "Gold", "precious_metal"),
    ("SI=F", "Silver", "precious_metal"),
    ("PL=F", "Platinum", "precious_metal"),
    ("PA=F", "Palladium", "precious_metal"),
    ("HG=F", "Copper", "base_metal"),
    ("ALI=F", "Aluminum", "base_metal"),
    ("ZN=F", "Zinc", "base_metal"),
    ("NI=F", "Nickel", "base_metal"),
    ("ZW=F", "Wheat", "agriculture"),
    ("ZC=F", "Corn", "agriculture"),
    ("ZS=F", "Soybeans", "agriculture"),
    ("KC=F", "Coffee", "agriculture"),
    ("SB=F", "Sugar", "agriculture"),
    ("CC=F", "Cocoa", "agriculture"),
    ("CT=F", "Cotton", "agriculture"),
    ("LE=F", "Live Cattle", "livestock"),
    ("HE=F", "Lean Hogs", "livestock"),
]

# --- Metals purchase by city (India gold/silver prices via proxy) ---
INDIA_METAL_CITIES = [
    "Mumbai", "Delhi", "Chennai", "Kolkata", "Bangalore",
    "Hyderabad", "Ahmedabad", "Pune", "Jaipur", "Lucknow",
    "Kochi", "Coimbatore", "Bhubaneswar", "Patna", "Chandigarh",
]

# --- Forex ---
FOREX: list[tuple[str, str, str]] = [
    ("USDINR=X", "USD/INR", "inr_cross"),
    ("EURINR=X", "EUR/INR", "inr_cross"),
    ("GBPINR=X", "GBP/INR", "inr_cross"),
    ("JPYINR=X", "JPY/INR", "inr_cross"),
    ("EURUSD=X", "EUR/USD", "major"),
    ("GBPUSD=X", "GBP/USD", "major"),
    ("USDJPY=X", "USD/JPY", "major"),
    ("USDCHF=X", "USD/CHF", "major"),
    ("AUDUSD=X", "AUD/USD", "major"),
    ("NZDUSD=X", "NZD/USD", "major"),
    ("USDCAD=X", "USD/CAD", "major"),
    ("USDCNY=X", "USD/CNY", "emerging"),
    ("USDSGD=X", "USD/SGD", "emerging"),
    ("USDHKD=X", "USD/HKD", "emerging"),
    ("DX-Y.NYB", "US Dollar Index (DXY)", "index"),
]

# --- US Equities (top 30) ---
US_EQUITIES: list[tuple[str, str, str]] = [
    ("AAPL", "Apple", "tech"),
    ("MSFT", "Microsoft", "tech"),
    ("GOOGL", "Alphabet", "tech"),
    ("AMZN", "Amazon", "tech"),
    ("NVDA", "NVIDIA", "tech"),
    ("META", "Meta Platforms", "tech"),
    ("TSLA", "Tesla", "auto"),
    ("BRK-B", "Berkshire Hathaway", "finance"),
    ("JPM", "JP Morgan Chase", "finance"),
    ("V", "Visa", "finance"),
    ("JNJ", "Johnson & Johnson", "healthcare"),
    ("UNH", "UnitedHealth", "healthcare"),
    ("XOM", "Exxon Mobil", "energy"),
    ("PG", "Procter & Gamble", "consumer"),
    ("MA", "Mastercard", "finance"),
    ("HD", "Home Depot", "retail"),
    ("CVX", "Chevron", "energy"),
    ("ABBV", "AbbVie", "healthcare"),
    ("MRK", "Merck", "healthcare"),
    ("PEP", "PepsiCo", "consumer"),
    ("KO", "Coca-Cola", "consumer"),
    ("COST", "Costco", "retail"),
    ("AVGO", "Broadcom", "tech"),
    ("TMO", "Thermo Fisher", "healthcare"),
    ("WMT", "Walmart", "retail"),
    ("DIS", "Walt Disney", "media"),
    ("NFLX", "Netflix", "media"),
    ("AMD", "AMD", "tech"),
    ("INTC", "Intel", "tech"),
    ("BA", "Boeing", "industrial"),
]

# --- US Options popular underlyings ---
US_OPTIONS_UNDERLYINGS: list[tuple[str, str, str]] = [
    ("SPY", "SPDR S&P 500 ETF", "index_etf"),
    ("QQQ", "Invesco QQQ", "index_etf"),
    ("IWM", "iShares Russell 2000", "index_etf"),
    ("AAPL", "Apple", "single_stock"),
    ("TSLA", "Tesla", "single_stock"),
    ("NVDA", "NVIDIA", "single_stock"),
    ("AMZN", "Amazon", "single_stock"),
    ("META", "Meta", "single_stock"),
    ("VIX", "CBOE Volatility Index", "volatility"),
]

# --- Crypto ---
CRYPTO: list[tuple[str, str, str]] = [
    ("BTC-USD", "Bitcoin", "layer1"),
    ("ETH-USD", "Ethereum", "layer1"),
    ("BNB-USD", "Binance Coin", "layer1"),
    ("SOL-USD", "Solana", "layer1"),
    ("XRP-USD", "Ripple", "layer1"),
    ("ADA-USD", "Cardano", "layer1"),
    ("DOGE-USD", "Dogecoin", "meme"),
    ("DOT-USD", "Polkadot", "layer1"),
    ("AVAX-USD", "Avalanche", "layer1"),
    ("MATIC-USD", "Polygon", "layer2"),
    ("LINK-USD", "Chainlink", "oracle"),
    ("UNI-USD", "Uniswap", "defi"),
    ("SHIB-USD", "Shiba Inu", "meme"),
    ("LTC-USD", "Litecoin", "layer1"),
    ("ATOM-USD", "Cosmos", "layer1"),
]

# --- US Bonds / Treasuries ---
US_BONDS: list[tuple[str, str, str]] = [
    ("^TNX", "US 10Y Treasury Yield", "treasury"),
    ("^TYX", "US 30Y Treasury Yield", "treasury"),
    ("^FVX", "US 5Y Treasury Yield", "treasury"),
    ("^IRX", "US 13-Week T-Bill", "treasury"),
    ("TLT", "iShares 20+ Year Treasury ETF", "etf"),
    ("IEF", "iShares 7-10 Year Treasury ETF", "etf"),
    ("SHY", "iShares 1-3 Year Treasury ETF", "etf"),
    ("BND", "Vanguard Total Bond Market ETF", "etf"),
    ("HYG", "iShares High Yield Corp Bond", "etf"),
    ("LQD", "iShares Investment Grade Corp", "etf"),
    ("AGG", "iShares Core US Aggregate Bond", "etf"),
    ("EMB", "iShares JP Morgan EM Bond", "etf"),
]

# --- US Futures ---
US_FUTURES: list[tuple[str, str, str]] = [
    ("ES=F", "E-mini S&P 500", "equity_index"),
    ("NQ=F", "E-mini NASDAQ 100", "equity_index"),
    ("YM=F", "E-mini Dow", "equity_index"),
    ("RTY=F", "E-mini Russell 2000", "equity_index"),
    ("ZB=F", "US Treasury Bond", "bond"),
    ("ZN=F", "10-Year T-Note", "bond"),
    ("ZF=F", "5-Year T-Note", "bond"),
    ("6E=F", "Euro FX Futures", "currency"),
    ("6J=F", "Japanese Yen Futures", "currency"),
    ("6B=F", "British Pound Futures", "currency"),
]

# --- Real Estate ---
REAL_ESTATE: list[tuple[str, str, str]] = [
    ("VNQ", "Vanguard Real Estate ETF", "us_reit"),
    ("IYR", "iShares US Real Estate ETF", "us_reit"),
    ("XLRE", "Real Estate Select Sector SPDR", "us_reit"),
    ("O", "Realty Income Corp", "us_reit"),
    ("AMT", "American Tower", "us_reit"),
    ("PLD", "Prologis", "us_reit"),
    ("SPG", "Simon Property Group", "us_reit"),
    ("EQIX", "Equinix", "us_reit"),
    ("CCI", "Crown Castle", "us_reit"),
    ("DLR", "Digital Realty", "us_reit"),
    ("PSA", "Public Storage", "us_reit"),
    ("WELL", "Welltower", "us_reit"),
    ("^CRSP-RE", "CRSP US RE Index Proxy", "index"),
    ("EMBASSY.NS", "Embassy REIT", "india_reit"),
    ("MINDSPACE.NS", "Mindspace REIT", "india_reit"),
    ("BROOKFIELD.NS", "Brookfield India REIT", "india_reit"),
]

# Master registry mapping category -> universe
# Each tuple: (yfinance_symbol, display_label, sub_category)
CATEGORY_REGISTRY: dict[str, list[tuple[str, str, str]]] = {
    "india_equity": INDIA_EQUITY_MAJOR,
    "india_mf": INDIA_MUTUAL_FUNDS,
    "india_bonds": INDIA_BONDS_ETFS,
    "india_index": INDIA_INDEX_FUTURES,
    "energy": ENERGY,
    "commodities": COMMODITIES,
    "forex": FOREX,
    "us_equity": US_EQUITIES,
    "us_options": US_OPTIONS_UNDERLYINGS,
    "crypto": CRYPTO,
    "us_bonds": US_BONDS,
    "us_futures": US_FUTURES,
    "real_estate": REAL_ESTATE,
}

# Extended registry — bulk universes loaded from cached JSON (universe_loader).
# Each entry: dict with symbol/name/sub_category/tags (+ optional nav/lot_size).
# Merged into API responses alongside the curated lists above.
EXTENDED_REGISTRY: dict[str, list[dict[str, Any]]] = {}


def _try_load_extended_registry() -> None:
    """Populate EXTENDED_REGISTRY from cached JSON files — safe if missing."""
    global EXTENDED_REGISTRY
    try:
        from backend.data import universe_registry as _ureg

        if _ureg.has_universe_cache():
            EXTENDED_REGISTRY = _ureg.build_full_registry()
            log.info(
                "Extended universe loaded: %d categories, %d total instruments",
                len(EXTENDED_REGISTRY),
                sum(len(v) for v in EXTENDED_REGISTRY.values()),
            )
    except Exception as e:
        log.warning("extended universe load failed: %s", e)


def _tags_for(sym: str) -> list[str]:
    """Return tags for any symbol (fast-path via universe_registry cache)."""
    try:
        from backend.data import universe_registry as _ureg

        return _ureg.tags_for_symbol(sym)
    except Exception:
        return []


_try_load_extended_registry()


# ---------------------------------------------------------------------------
# Fetching helpers
# ---------------------------------------------------------------------------

def _yf_batch_quotes(
    symbols: list[str],
) -> dict[str, dict[str, Any]]:
    """Fetch latest price for a batch of yfinance symbols."""
    out: dict[str, dict[str, Any]] = {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            fi = t.fast_info
            last = None
            if isinstance(fi, dict):
                last = fi.get("last_price") or fi.get("lastPrice")
            else:
                last = (
                    getattr(fi, "last_price", None)
                    or getattr(fi, "lastPrice", None)
                )
            if last is None:
                hist = t.history(period="5d")
                if hist is not None and not hist.empty:
                    last = float(hist["Close"].iloc[-1])
            currency = (
                fi.get("currency")
                if isinstance(fi, dict)
                else getattr(fi, "currency", None)
            )
            prev_close = (
                fi.get("previous_close")
                if isinstance(fi, dict)
                else getattr(fi, "previous_close", None)
            ) or (
                fi.get("previousClose")
                if isinstance(fi, dict)
                else getattr(fi, "previousClose", None)
            )
            change_pct = None
            if last and prev_close:
                try:
                    change_pct = round(
                        ((float(last) / float(prev_close)) - 1) * 100, 2
                    )
                except (TypeError, ValueError, ZeroDivisionError):
                    pass
            out[sym] = {
                "last": float(last) if last is not None else None,
                "currency": currency,
                "prev_close": (
                    float(prev_close) if prev_close is not None else None
                ),
                "change_pct": change_pct,
            }
        except Exception as e:
            log.warning("yf quote failed for %s: %s", sym, e)
            out[sym] = {"last": None, "currency": None, "error": str(e)}
    return out


def fetch_category(
    category: str,
    limit: int | None = None,
    offset: int = 0,
    tag: str | None = None,
    fetch_quotes: bool = True,
) -> dict[str, Any]:
    """
    Fetch all instruments in a category with live quotes.

    category: category id (curated or extended).
    limit/offset: pagination for huge universes (NSE equity = 2000+).
    tag: optional index-membership filter (e.g. "NIFTY50", "FNO").
    fetch_quotes: set False for skeleton listing (no yfinance calls).
    """
    # First, assemble the full universe for this category
    curated = CATEGORY_REGISTRY.get(category)
    extended = EXTENDED_REGISTRY.get(category)

    universe_dicts: list[dict[str, Any]] = []
    if curated:
        for sym, label, sub_cat in curated:
            universe_dicts.append({
                "symbol": sym,
                "name": label,
                "sub_category": sub_cat,
                "tags": _tags_for(sym),
            })
    if extended:
        universe_dicts.extend(extended)

    if not universe_dicts:
        return {"error": f"unknown category: {category}"}

    # Tag filter
    if tag:
        tag_u = tag.upper()
        universe_dicts = [
            u for u in universe_dicts if tag_u in (u.get("tags") or [])
        ]

    total = len(universe_dicts)

    # Pagination
    if limit is not None:
        universe_dicts = universe_dicts[offset : offset + limit]

    if fetch_quotes:
        symbols = [u["symbol"] for u in universe_dicts]
        # Cap live quote fetch at 100 symbols — avoid yf rate limits on huge cats
        symbols_to_quote = symbols[:100]
        quotes = _yf_batch_quotes(symbols_to_quote)
    else:
        quotes = {}

    instruments = []
    for u in universe_dicts:
        q = quotes.get(u["symbol"], {})
        instruments.append(
            {
                "symbol": u["symbol"],
                "name": u.get("name") or u["symbol"],
                "sub_category": u.get("sub_category"),
                "tags": u.get("tags") or [],
                "last": q.get("last"),
                "currency": q.get("currency"),
                "prev_close": q.get("prev_close"),
                "change_pct": q.get("change_pct"),
                "error": q.get("error"),
            }
        )
    return {
        "category": category,
        "count": len(instruments),
        "total": total,
        "offset": offset,
        "limit": limit,
        "tag_filter": tag,
        "instruments": instruments,
    }


def fetch_single_quote(symbol: str) -> dict[str, Any]:
    """Detailed quote for a single symbol."""
    try:
        t = yf.Ticker(symbol)
        info = {}
        try:
            info = t.info or {}
        except Exception:
            pass
        fi = t.fast_info
        last = None
        if isinstance(fi, dict):
            last = fi.get("last_price") or fi.get("lastPrice")
        else:
            last = (
                getattr(fi, "last_price", None)
                or getattr(fi, "lastPrice", None)
            )
        if last is None:
            hist = t.history(period="5d")
            if hist is not None and not hist.empty:
                last = float(hist["Close"].iloc[-1])
        currency = (
            fi.get("currency")
            if isinstance(fi, dict)
            else getattr(fi, "currency", None)
        )
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        open_ = info.get("regularMarketOpen") or info.get("open")
        day_low = info.get("dayLow") or info.get("regularMarketDayLow")
        day_high = info.get("dayHigh") or info.get("regularMarketDayHigh")
        change_pct = None
        if last is not None and prev_close:
            try:
                change_pct = (float(last) - float(prev_close)) / float(prev_close) * 100.0
            except Exception:
                change_pct = None
        return {
            "symbol": symbol,
            "last": float(last) if last is not None else None,
            "currency": currency,
            "name": info.get("shortName") or info.get("longName"),
            "long_name": info.get("longName"),
            "exchange": info.get("exchange") or info.get("fullExchangeName"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "peg_ratio": info.get("pegRatio"),
            "eps": info.get("trailingEps"),
            "forward_eps": info.get("forwardEps"),
            "book_value": info.get("bookValue"),
            "dividend_yield": info.get("dividendYield"),
            "dividend_rate": info.get("dividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            "beta": info.get("beta"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "50d_avg": info.get("fiftyDayAverage"),
            "200d_avg": info.get("twoHundredDayAverage"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "avg_volume": info.get("averageVolume"),
            "open": open_,
            "prev_close": prev_close,
            "day_low": day_low,
            "day_high": day_high,
            "change_pct": change_pct,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "description": info.get("longBusinessSummary") or info.get("businessSummary"),
            "earnings_date": info.get("earningsDate"),
            "recommendation": info.get("recommendationKey"),
            "target_mean_price": info.get("targetMeanPrice"),
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "gross_margin": info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "total_revenue": info.get("totalRevenue"),
            "ebitda": info.get("ebitda"),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def search_symbol(query: str) -> list[dict[str, Any]]:
    """Search across curated + extended universes by symbol or name."""
    q = query.lower()
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Curated lists first
    for cat, universe in CATEGORY_REGISTRY.items():
        for sym, label, sub_cat in universe:
            if q in sym.lower() or q in label.lower():
                if sym in seen:
                    continue
                seen.add(sym)
                results.append(
                    {
                        "symbol": sym,
                        "name": label,
                        "category": cat,
                        "sub_category": sub_cat,
                        "tags": _tags_for(sym),
                    }
                )
                if len(results) >= 50:
                    return results

    # Extended (big) lists
    for cat, rows in EXTENDED_REGISTRY.items():
        for r in rows:
            sym = r.get("symbol") or ""
            name = r.get("name") or ""
            if q in sym.lower() or q in name.lower():
                if sym in seen:
                    continue
                seen.add(sym)
                results.append(
                    {
                        "symbol": sym,
                        "name": name,
                        "category": cat,
                        "sub_category": r.get("sub_category"),
                        "tags": r.get("tags") or [],
                    }
                )
                if len(results) >= 50:
                    return results
    return results


def india_metal_prices_by_city() -> dict[str, Any]:
    """
    Gold/silver prices by Indian city. Uses gold futures + city premium model.
    Real per-city pricing requires jeweller association APIs or scraping;
    this provides futures-based estimates with typical city premiums.
    """
    quotes = _yf_batch_quotes(["GC=F", "SI=F", "USDINR=X"])
    gold_usd = (quotes.get("GC=F") or {}).get("last")
    silver_usd = (quotes.get("SI=F") or {}).get("last")
    usdinr = (quotes.get("USDINR=X") or {}).get("last")

    if not all([gold_usd, silver_usd, usdinr]):
        return {
            "error": "missing_price_data",
            "gold_usd_oz": gold_usd,
            "silver_usd_oz": silver_usd,
            "usdinr": usdinr,
        }

    gold_inr_per_gram = (gold_usd * usdinr) / 31.1035
    silver_inr_per_gram = (silver_usd * usdinr) / 31.1035
    gold_inr_per_10g = gold_inr_per_gram * 10

    city_premiums = {
        "Mumbai": 0, "Delhi": 50, "Chennai": 100,
        "Kolkata": 80, "Bangalore": 60, "Hyderabad": 70,
        "Ahmedabad": 40, "Pune": 30, "Jaipur": 90,
        "Lucknow": 110, "Kochi": 120, "Coimbatore": 100,
        "Bhubaneswar": 130, "Patna": 140, "Chandigarh": 60,
    }
    cities = []
    for city in INDIA_METAL_CITIES:
        prem = city_premiums.get(city, 0)
        cities.append({
            "city": city,
            "gold_24k_per_10g": round(gold_inr_per_10g + prem, 2),
            "gold_22k_per_10g": round(
                (gold_inr_per_10g + prem) * 22 / 24, 2
            ),
            "silver_per_kg": round(silver_inr_per_gram * 1000 + prem * 5, 2),
            "premium_inr": prem,
        })
    return {
        "reference": {
            "gold_usd_per_oz": round(gold_usd, 2),
            "silver_usd_per_oz": round(silver_usd, 2),
            "usdinr": round(usdinr, 4),
            "gold_inr_per_10g_base": round(gold_inr_per_10g, 2),
        },
        "cities": cities,
    }


def list_categories() -> list[dict[str, Any]]:
    """Return all supported categories (curated + extended) with counts."""
    cats: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cat, universe in CATEGORY_REGISTRY.items():
        seen.add(cat)
        cats.append(
            {
                "id": cat,
                "label": cat.replace("_", " ").title(),
                "count": len(universe),
                "kind": "curated",
            }
        )
    for cat, rows in EXTENDED_REGISTRY.items():
        if cat in seen:
            continue
        cats.append(
            {
                "id": cat,
                "label": cat.replace("_", " ").title(),
                "count": len(rows),
                "kind": "extended",
            }
        )
    return cats


def reload_extended_registry() -> dict[str, int]:
    """Re-read the universe JSONs after a refresh run."""
    from backend.data import universe_registry as _ureg

    _ureg.invalidate_cache()
    _try_load_extended_registry()
    return {cat: len(rows) for cat, rows in EXTENDED_REGISTRY.items()}


def list_available_tags() -> list[dict[str, Any]]:
    """All index/membership tags found across the current universe, with counts."""
    from backend.data.universe_registry import label_for_tag

    counts: dict[str, int] = {}
    for _, rows in EXTENDED_REGISTRY.items():
        for r in rows:
            for t in r.get("tags") or []:
                counts[t] = counts.get(t, 0) + 1
    for cat, universe in CATEGORY_REGISTRY.items():
        for sym, _, _ in universe:
            for t in _tags_for(sym):
                counts[t] = counts.get(t, 0) + 1
    return [
        {"tag": t, "label": label_for_tag(t), "count": c}
        for t, c in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    ]


def fetch_price_history(
    symbol: str, period: str = "6mo", interval: str = "1d",
) -> dict[str, Any]:
    """Return OHLCV time series for charting."""
    allowed_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "max"}
    allowed_intervals = {"1d", "1wk", "1mo"}
    if period not in allowed_periods:
        period = "6mo"
    if interval not in allowed_intervals:
        interval = "1d"
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period, interval=interval)
        if hist is None or hist.empty:
            return {"symbol": symbol, "points": [], "error": "No data"}
        points: list[dict[str, Any]] = []
        for ts, row in hist.iterrows():
            points.append({
                "date": ts.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if row["Volume"] else 0,
            })
        return {"symbol": symbol, "period": period, "interval": interval, "points": points}
    except Exception as e:
        return {"symbol": symbol, "points": [], "error": str(e)}


def fetch_symbol_news(symbol: str) -> dict[str, Any]:
    """Fetch news for a symbol from available sources."""
    from backend.config import get_settings
    settings = get_settings()
    articles: list[dict[str, Any]] = []

    clean_sym = symbol.replace(".NS", "").replace(".BO", "").split("=")[0].split("-")[0]

    if settings.finnhub_api_key:
        try:
            from backend.data.fetchers import finnhub_fetcher
            news = finnhub_fetcher.company_news(clean_sym)
            if isinstance(news, list):
                for n in news[:5]:
                    articles.append({
                        "title": n.get("headline", ""),
                        "url": n.get("url", ""),
                        "source": n.get("source", "Finnhub"),
                        "date": n.get("datetime", ""),
                        "summary": n.get("summary", "")[:200],
                    })
        except Exception:
            pass

    if settings.marketaux_key and len(articles) < 8:
        try:
            from backend.data.fetchers import marketaux_fetcher
            resp = marketaux_fetcher.sentiment_by_symbol(clean_sym, limit=5)
            for n in resp.get("data", [])[:5]:
                articles.append({
                    "title": n.get("title", ""),
                    "url": n.get("url", ""),
                    "source": "Marketaux",
                    "date": n.get("published_at", ""),
                    "summary": n.get("description", "")[:200],
                    "sentiment": n.get("sentiment_score"),
                })
        except Exception:
            pass

    if settings.news_api_key and len(articles) < 8:
        try:
            from backend.data.fetchers import newsapi_fetcher
            resp = newsapi_fetcher.search_news(clean_sym, page_size=5)
            for n in resp.get("articles", [])[:5]:
                articles.append({
                    "title": n.get("title", ""),
                    "url": n.get("url", ""),
                    "source": (n.get("source") or {}).get("name", "NewsAPI"),
                    "date": n.get("publishedAt", ""),
                    "summary": (n.get("description") or "")[:200],
                })
        except Exception:
            pass

    return {"symbol": symbol, "articles": articles}
