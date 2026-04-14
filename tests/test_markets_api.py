from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_categories_endpoint():
    r = client.get("/api/markets/categories")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 10
    ids = {c["id"] for c in body}
    assert "india_equity" in ids
    assert "crypto" in ids
    assert "energy" in ids


def test_search_endpoint():
    r = client.get("/api/markets/search?q=bitcoin")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert any("BTC" in item["symbol"] for item in body)


def test_invalid_category_returns_422():
    r = client.get("/api/markets/category/nonexistent")
    assert r.status_code == 422
