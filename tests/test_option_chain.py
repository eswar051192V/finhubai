from backend.engines.option_chain import max_pain, pcr


def test_pcr_balanced_synthetic():
    rows = [
        {"strikePrice": 100, "CE": {"openInterest": 1000}, "PE": {"openInterest": 1000}},
        {"strikePrice": 110, "CE": {"openInterest": 500}, "PE": {"openInterest": 500}},
    ]
    out = pcr(rows)
    assert out["pcr_oi"] == 1.0


def test_max_pain_finds_strike():
    rows = [
        {"strikePrice": 100, "CE": {"openInterest": 2000}, "PE": {"openInterest": 100}},
        {"strikePrice": 110, "CE": {"openInterest": 100}, "PE": {"openInterest": 2000}},
    ]
    out = max_pain(rows, 105)
    assert out["max_pain"] is not None
