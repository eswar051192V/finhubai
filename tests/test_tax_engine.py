from datetime import date, timedelta

from backend.engines import tax_engine


def test_when_to_sell_still_short_term():
    purchase = date(2025, 1, 1)
    as_of = purchase + timedelta(days=30)
    out = tax_engine.when_to_sell_analysis(
        purchase_date=purchase,
        as_of=as_of,
        buy_price=100,
        last_price=110,
        quantity=1,
    )
    assert out["is_long_term"] is False
    assert out["days_to_ltcg"] > 0


def test_when_to_sell_long_term():
    purchase = date(2023, 1, 1)
    as_of = date(2025, 1, 15)
    out = tax_engine.when_to_sell_analysis(
        purchase_date=purchase,
        as_of=as_of,
        buy_price=100,
        last_price=200,
        quantity=1,
    )
    assert out["is_long_term"] is True
