"""
Ollama AI Engine — natural language queries, market analysis,
and research assistance powered by local LLM.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.config import get_settings

log = logging.getLogger(__name__)


def _ollama_url() -> str:
    return get_settings().ollama_url.rstrip("/")


def is_available() -> dict[str, Any]:
    """Check if Ollama is running and which models are loaded."""
    try:
        r = httpx.get(f"{_ollama_url()}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        models = [m["name"] for m in data.get("models", [])]
        return {"available": True, "models": models}
    except Exception as e:
        return {"available": False, "error": str(e)}


def pull_model(model: str) -> dict[str, Any]:
    """Tell Ollama to pull a model (can take minutes for first download)."""
    try:
        r = httpx.post(
            f"{_ollama_url()}/api/pull",
            json={"name": model},
            timeout=600,
        )
        return {"status": "pulled", "model": model, "response": r.text[:500]}
    except Exception as e:
        return {"error": str(e), "model": model}


def chat(
    prompt: str,
    system: str = (
        "You are FinanceLab AI, a financial analysis assistant. "
        "You have access to Indian and US market data, tax rules, "
        "and trading concepts. Be precise with numbers and cite data sources."
    ),
    model: str | None = None,
) -> dict[str, Any]:
    """Send a chat message to the local Ollama model."""
    settings = get_settings()
    model_name = model or settings.ollama_model
    try:
        r = httpx.post(
            f"{_ollama_url()}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "system": system,
                "stream": False,
            },
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return {
            "model": model_name,
            "response": data.get("response", ""),
            "eval_count": data.get("eval_count"),
            "eval_duration_ns": data.get("eval_duration"),
        }
    except httpx.ConnectError:
        return {
            "error": "Ollama not running. Start with: ollama serve",
            "model": model_name,
        }
    except Exception as e:
        return {"error": str(e), "model": model_name}


def analyze_symbol(symbol: str) -> dict[str, Any]:
    """Ask AI for analysis of a specific stock/instrument."""
    prompt = (
        f"Analyze {symbol} for me. Cover:\n"
        f"1. What the company/instrument does\n"
        f"2. Recent performance trends\n"
        f"3. Key risks and catalysts\n"
        f"4. Valuation assessment (is it cheap or expensive?)\n"
        f"5. Recommendation: should a retail investor consider it?\n"
        f"Be concise — 3-4 sentences per point."
    )
    return chat(prompt)


def explain_concept(concept: str) -> dict[str, Any]:
    """Explain a financial concept in simple terms."""
    prompt = (
        f"Explain '{concept}' in simple terms for an Indian retail investor. "
        f"Include: what it is, why it matters, how to use it in practice, "
        f"and any India-specific rules or tax implications. "
        f"Keep it under 200 words."
    )
    return chat(prompt)


def market_query(query: str) -> dict[str, Any]:
    """Answer any natural language market question."""
    return chat(query)
