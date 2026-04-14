from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_cost_calculator():
    r = client.post(
        "/api/cost-calculator",
        json={
            "broker": "zerodha",
            "segment": "equity_intraday",
            "side": "sell",
            "quantity": 1,
            "price": 1000,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["currency"] == "INR"
    assert "breakdown" in body
