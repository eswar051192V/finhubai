"""Aggregate sentiment: FII/DII-first, Finnhub news keywords, optional FinBERT."""

from __future__ import annotations

import math
from typing import Any

from backend.config import get_settings
from backend.data.fetchers import finnhub_fetcher, nse_fetcher, yfinance_fetcher


def _news_keyword_score(headlines: list[str]) -> float:
    if not headlines:
        return 0.0
    pos = ("beat", "growth", "upgrade", "record", "surge", "win", "bull", "strong")
    neg = ("miss", "downgrade", "probe", "fraud", "loss", "cut", "bear", "weak", "ban")
    score = 0.0
    for h in headlines:
        low = h.lower()
        score += sum(1 for w in pos if w in low)
        score -= sum(1 for w in neg if w in low)
    return max(-1.0, min(1.0, score / max(5, len(headlines) * 0.5)))


def _finbert_score(texts: list[str]) -> float | None:
    settings = get_settings()
    if not settings.sentiment_finbert_enabled or not texts:
        return None
    try:
        from transformers import pipeline  # type: ignore
    except ImportError:
        return None
    try:
        clf = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
        )
    except Exception:
        return None
    scores: list[float] = []
    for t in texts[:8]:
        out = clf(t[:512])[0]
        label = out.get("label", "").lower()
        conf = float(out.get("score", 0.0))
        if "pos" in label:
            scores.append(conf)
        elif "neg" in label:
            scores.append(-conf)
        else:
            scores.append(0.0)
    if not scores:
        return None
    return max(-1.0, min(1.0, sum(scores) / len(scores)))


def composite_sentiment(ticker: str) -> dict[str, Any]:
    quote = yfinance_fetcher.quote_summary(ticker)
    news = finnhub_fetcher.company_news(ticker.replace(".NS", "").upper(), days=7)
    headlines = [str(i.get("headline", "")) for i in news.get("items") or [] if i.get("headline")]

    fii = nse_fetcher.fii_dii_data()
    parsed = (
        nse_fetcher.parse_fii_dii_net_crores(fii)
        if fii.get("raw")
        else {"fii_net_crores": None, "dii_net_crores": None, "parse_note": "nse_unavailable"}
    )

    fii_net = parsed.get("fii_net_crores")
    dii_net = parsed.get("dii_net_crores")
    flow = 0.0
    if fii_net is not None and dii_net is not None:
        # Normalize roughly to -1..1 using tanh on net sum
        flow = math.tanh((fii_net + dii_net) / 5000.0)
    elif fii_net is not None:
        flow = math.tanh(fii_net / 3000.0)

    news_score = _news_keyword_score(headlines)
    finbert = _finbert_score(headlines)

    # Weights: FII/DII dominant
    w_flow, w_news, w_fb = 0.55, 0.35, 0.10
    if finbert is None:
        w_flow, w_news = 0.6, 0.4
        w_fb = 0.0
    composite = w_flow * flow + w_news * news_score + (w_fb * finbert if finbert is not None else 0)
    composite = max(-1.0, min(1.0, composite))

    label = "neutral"
    if composite > 0.25:
        label = "constructive"
    elif composite < -0.25:
        label = "cautious"

    return {
        "ticker": ticker,
        "score": round(composite, 4),
        "label": label,
        "components": {
            "fii_dii_flow_proxy": round(flow, 4),
            "news_keyword": round(news_score, 4),
            "finbert": None if finbert is None else round(finbert, 4),
            "fii_net_crores": fii_net,
            "dii_net_crores": dii_net,
        },
        "quote": quote,
        "news_error": news.get("error"),
        "headlines_sample": headlines[:5],
    }
