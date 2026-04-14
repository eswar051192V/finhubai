from backend.data.fetchers.markets_fetcher import (
    CATEGORY_REGISTRY,
    list_categories,
    search_symbol,
)


def test_all_categories_have_entries():
    for cat, universe in CATEGORY_REGISTRY.items():
        assert len(universe) > 0, f"{cat} is empty"


def test_list_categories_returns_all():
    cats = list_categories()
    ids = {c["id"] for c in cats}
    assert "india_equity" in ids
    assert "energy" in ids
    assert "crypto" in ids
    assert "real_estate" in ids
    assert "us_equity" in ids
    assert "forex" in ids
    assert "commodities" in ids
    assert "us_bonds" in ids
    assert "us_futures" in ids


def test_search_finds_reliance():
    results = search_symbol("reliance")
    assert len(results) >= 1
    assert any(r["symbol"] == "RELIANCE.NS" for r in results)


def test_search_finds_apple():
    results = search_symbol("apple")
    assert len(results) >= 1
    assert any(r["symbol"] == "AAPL" for r in results)


def test_search_finds_gold():
    results = search_symbol("gold")
    assert len(results) >= 1


def test_search_case_insensitive():
    r1 = search_symbol("BITCOIN")
    r2 = search_symbol("bitcoin")
    assert len(r1) == len(r2)


def test_search_limits_results():
    results = search_symbol("a")
    assert len(results) <= 50
