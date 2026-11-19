"""Tests for IsolationForest + z-score anomaly detection."""

import pandas as pd
from app.ml.anomaly import anomaly_detector


def test_anomaly_detection_catches_spikes():
    # Construct a dataset of typical expenses with 2 obvious spikes
    data = []
    # 30 normal food transactions around ₹300-500
    for i in range(30):
        data.append({
            "id": i + 1,
            "date": "2026-11-01",
            "description": f"UPI/SWIGGY MEAL #{i}",
            "amount": 350.0 + (i % 5) * 20,
            "type": "expense",
            "category": "Food & Dining",
        })

    # Normal groceries
    for i in range(20):
        data.append({
            "id": 100 + i,
            "date": "2026-11-02",
            "description": f"BIGBASKET GROCERY #{i}",
            "amount": 1200.0 + (i % 4) * 100,
            "type": "expense",
            "category": "Groceries",
        })

    # Planted huge spike anomaly in food: ₹9,500 (vs usual ₹350)
    data.append({
        "id": 999,
        "date": "2026-11-03",
        "description": "UPI/SWIGGY HUGE BANQUET CATERING",
        "amount": 9500.0,
        "type": "expense",
        "category": "Food & Dining",
    })

    df = pd.DataFrame(data)
    results = anomaly_detector.detect(df)
    assert len(results) > 0

    flagged_ids = {r["transaction_id"]: r["reason"] for r in results if r["is_anomaly"]}
    assert 999 in flagged_ids, "Planted outlier ₹9,500 must be flagged as anomaly"
    assert "higher than your usual" in flagged_ids[999] or "spending" in flagged_ids[999].lower()

