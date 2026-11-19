"""Tests for recommendation engine, health score calculation, and what-if simulation."""

import pandas as pd
from app.ml.recommendations import recommendation_engine


def test_recommendation_and_health_score_engine():
    data = [
        {"date": "2026-11-01", "description": "SALARY", "amount": 80000.0, "type": "income", "category": "Income"},
        {"date": "2026-11-02", "description": "RENT", "amount": 18000.0, "type": "expense", "category": "Rent & Housing"},
        {"date": "2026-11-05", "description": "SWIGGY FOOD", "amount": 9500.0, "type": "expense", "category": "Food & Dining"},
        {"date": "2026-11-10", "description": "AMAZON SHOPPING", "amount": 8500.0, "type": "expense", "category": "Shopping"},
        {"date": "2026-11-15", "description": "NETFLIX", "amount": 1800.0, "type": "expense", "category": "Entertainment & Subscriptions"},
    ]
    df = pd.DataFrame(data)

    # 1. Health Score
    health = recommendation_engine.calculate_health_score(df)
    assert 0 <= health["score"] <= 100
    assert health["grade"] in ["A+", "A", "B", "C", "D", "F"]
    assert "savings_rate" in health["breakdown"]

    # 2. Recommendations
    recs = recommendation_engine.generate_recommendations(df)
    assert len(recs) >= 1
    # Check food delivery or shopping recommendation generated
    titles = [r["title"] for r in recs]
    assert any("Food" in t or "Shopping" in t for t in titles)

    # 3. What-If Simulation
    sim = recommendation_engine.what_if_simulation(
        df,
        adjustments={"Food & Dining": 20.0, "Shopping": 25.0},
    )
    assert sim["current_monthly_spend"] > 0
    assert sim["monthly_savings"] > 0
    assert sim["yearly_savings"] == sim["monthly_savings"] * 12
    assert sim["projected_monthly_spend"] < sim["current_monthly_spend"]

