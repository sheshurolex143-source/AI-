"""Tests for transaction categorizer model accuracy (>90%) and inference outputs."""

import pytest
from app.ml.categorizer import categorizer


def test_model_metrics_accuracy():
    metrics = categorizer.get_metrics()
    assert metrics is not None, "Model metrics must exist."
    assert metrics["accuracy"] >= 0.90, f"Expected accuracy >= 90%, got {metrics['accuracy'] * 100}%"
    assert len(metrics["categories"]) == 13
    assert metrics["feature_count"] > 1000


def test_categorizer_predictions():
    # Test food prediction
    food_pred = categorizer.predict("UPI/SWIGGY*ORDER 9921 BLR")
    assert food_pred["category"] == "Food & Dining"
    assert food_pred["confidence"] > 0.60
    assert food_pred["needs_review"] is False
    assert len(food_pred["alternatives"]) <= 3

    # Test groceries
    groc_pred = categorizer.predict("POS 4410 BIGBASKET RETAIL")
    assert groc_pred["category"] == "Groceries"

    # Test bill / EMI
    bill_pred = categorizer.predict("NACH DEBIT HDFC HOME LOAN EMI")
    assert bill_pred["category"] in ["Bills & Utilities", "Rent & Housing"]

    # Test income
    inc_pred = categorizer.predict("NEFT MONTHLY SALARY CREDIT INFOSYS")
    assert inc_pred["category"] == "Income"

