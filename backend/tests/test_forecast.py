"""Tests for weighted moving average + linear trend spending forecaster."""

import pandas as pd
from app.ml.forecast import forecaster


def test_forecast_calculation():
    # 3 months of consistent data
    records = []
    # Month 1: 2026-08
    records.append({"date": "2026-08-05", "category": "Food & Dining", "amount": 5000.0, "type": "expense"})
    records.append({"date": "2026-08-10", "category": "Shopping", "amount": 3000.0, "type": "expense"})

    # Month 2: 2026-09
    records.append({"date": "2026-09-05", "category": "Food & Dining", "amount": 5500.0, "type": "expense"})
    records.append({"date": "2026-09-10", "category": "Shopping", "amount": 3200.0, "type": "expense"})

    # Month 3: 2026-10
    records.append({"date": "2026-10-05", "category": "Food & Dining", "amount": 6000.0, "type": "expense"})
    records.append({"date": "2026-10-10", "category": "Shopping", "amount": 3500.0, "type": "expense"})

    df = pd.DataFrame(records)
    res = forecaster.forecast(df)

    assert "forecasts" in res
    assert res["total_predicted"] > 0
    assert res["total_confidence_low"] <= res["total_predicted"] <= res["total_confidence_high"]

    food_fc = next((f for f in res["forecasts"] if f["category"] == "Food & Dining"), None)
    assert food_fc is not None
    assert food_fc["predicted_next_month"] > 5000
    assert food_fc["trend"] in ["increasing", "stable"]

