from backend.engines.broker_costs import Broker, Segment, Side, calculate_true_cost


def test_zerodha_delivery_buy_positive_quantity():
    out = calculate_true_cost(Broker.ZERODHA, Segment.EQUITY_DELIVERY, Side.BUY, 10, 1000)
    assert out["currency"] == "INR"
    assert out["breakdown"]["total"] >= 0
    assert out["turnover"] == 10_000


def test_zerodha_delivery_sell_includes_stt():
    out = calculate_true_cost(Broker.ZERODHA, Segment.EQUITY_DELIVERY, Side.SELL, 10, 1000)
    assert out["breakdown"]["stt"] > 0


def test_ibkr_returns_usd_bucket():
    out = calculate_true_cost(Broker.IBKR, Segment.EQUITY_DELIVERY, Side.BUY, 10, 100)
    assert out["currency"] == "USD"
