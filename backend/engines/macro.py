"""
Macro Regime Classifier — four-regime model.
Goldilocks / Reflation / Stagflation / Deflation
Updated from FRED data and market indicators.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from backend.data.fetchers import fred_fetcher

log = logging.getLogger(__name__)

REGIMES = {
    "goldilocks": {
        "label": "Goldilocks",
        "description": "Moderate growth, low inflation. Best for equities.",
        "favors": ["equity", "growth", "tech"],
        "avoids": ["gold", "commodities"],
    },
    "reflation": {
        "label": "Reflation",
        "description": "Rising growth and inflation. Cyclicals and commodities benefit.",
        "favors": ["commodities", "energy", "financials", "value"],
        "avoids": ["long_duration_bonds", "growth"],
    },
    "stagflation": {
        "label": "Stagflation",
        "description": "Slowing growth with high inflation. Worst for most assets.",
        "favors": ["gold", "cash", "real_assets"],
        "avoids": ["equity", "bonds", "growth"],
    },
    "deflation": {
        "label": "Deflation",
        "description": "Falling growth and inflation. Bonds rally.",
        "favors": ["long_duration_bonds", "quality", "defensive"],
        "avoids": ["commodities", "cyclicals", "small_cap"],
    },
}

FRED_SERIES = {
    "gdp_growth": "A191RL1Q225SBEA",
    "cpi_yoy": "CPIAUCSL",
    "unemployment": "UNRATE",
    "fed_funds": "FEDFUNDS",
    "yield_10y": "DGS10",
    "yield_2y": "DGS2",
    "yield_spread": "T10Y2Y",
    "vix": "VIXCLS",
}


def classify_regime(
    gdp_growth: Optional[float] = None,
    inflation: Optional[float] = None,
) -> dict[str, Any]:
    """
    Classify the current macro regime.
    gdp_growth: annualized GDP growth rate (e.g. 2.5 = 2.5%)
    inflation: YoY CPI change (e.g. 3.2 = 3.2%)
    """
    growth_threshold = 2.0
    inflation_threshold = 3.0

    if gdp_growth is None:
        gdp_growth = 2.5
    if inflation is None:
        inflation = 2.5

    if gdp_growth >= growth_threshold and inflation < inflation_threshold:
        regime = "goldilocks"
    elif gdp_growth >= growth_threshold and inflation >= inflation_threshold:
        regime = "reflation"
    elif gdp_growth < growth_threshold and inflation >= inflation_threshold:
        regime = "stagflation"
    else:
        regime = "deflation"

    return {
        "regime": regime,
        "inputs": {"gdp_growth": gdp_growth, "inflation": inflation},
        **REGIMES[regime],
    }


def fetch_macro_dashboard() -> dict[str, Any]:
    """Fetch latest macro indicators from FRED and classify regime."""
    indicators: dict[str, Any] = {}
    for name, series_id in FRED_SERIES.items():
        try:
            obs = fred_fetcher.latest_observation(series_id)
            indicators[name] = obs
        except Exception as e:
            indicators[name] = {"error": str(e)}

    gdp_val = None
    cpi_val = None
    if isinstance(indicators.get("gdp_growth"), dict):
        gdp_val = indicators["gdp_growth"].get("value")
    if isinstance(indicators.get("cpi_yoy"), dict):
        cpi_val = indicators["cpi_yoy"].get("value")

    regime = classify_regime(
        gdp_growth=float(gdp_val) if gdp_val else None,
        inflation=float(cpi_val) if cpi_val else None,
    )
    return {
        "regime": regime,
        "indicators": indicators,
    }
