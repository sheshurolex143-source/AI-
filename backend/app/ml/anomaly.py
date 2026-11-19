"""Anomaly detection using IsolationForest + per-category z-score."""

import re
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder


class AnomalyDetector:
    """Detects anomalous transactions using ensemble methods."""

    def __init__(self):
        """Initialize the anomaly detector."""
        self.contamination = 0.05

    def _normalize_merchant(self, description: str) -> str:
        """Extract and normalize merchant name from description."""
        desc = description.upper()
        desc = re.sub(r'(UPI|POS|NEFT|IMPS|NACH|DEBIT|CREDIT|CARD|REF|TXN|INR)\s*/?', '', desc)
        desc = re.sub(r'[0-9*#]+', '', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        # Take first meaningful word(s)
        parts = [p for p in desc.split() if len(p) > 2]
        return ' '.join(parts[:2]).title() if parts else description[:20].title()

    def detect(self, transactions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in transaction data.

        Args:
            transactions_df: DataFrame with columns: id, amount, category, date, description, type

        Returns:
            List of dicts with transaction_id, is_anomaly, reason.
        """
        if transactions_df.empty or len(transactions_df) < 10:
            return []

        # Only analyze expenses for anomalies
        expenses = transactions_df[transactions_df["type"] == "expense"].copy()
        if expenses.empty or len(expenses) < 5:
            return []

        results = []

        # ── Feature Engineering ──
        expenses = expenses.copy()
        expenses["log_amount"] = np.log1p(expenses["amount"].values)
        expenses["day_of_week"] = pd.to_datetime(expenses["date"]).dt.dayofweek
        expenses["is_weekend"] = (expenses["day_of_week"] >= 5).astype(int)
        expenses["merchant"] = expenses["description"].apply(self._normalize_merchant)

        # Merchant frequency
        merchant_counts = expenses["merchant"].value_counts().to_dict()
        expenses["merchant_freq"] = expenses["merchant"].map(merchant_counts)

        # Category encoding
        le = LabelEncoder()
        expenses["category_encoded"] = le.fit_transform(expenses["category"].fillna("Other"))

        # ── IsolationForest ──
        feature_cols = ["log_amount", "category_encoded", "day_of_week", "is_weekend", "merchant_freq"]
        X = expenses[feature_cols].values

        iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
        )
        iso_predictions = iso_forest.fit_predict(X)  # -1 for anomalies

        # ── Per-category Z-score ──
        category_stats = expenses.groupby("category")["amount"].agg(["mean", "std"]).reset_index()
        category_stats.columns = ["category", "cat_mean", "cat_std"]
        category_stats["cat_std"] = category_stats["cat_std"].fillna(0).replace(0, 1)

        expenses = expenses.merge(category_stats, on="category", how="left")
        expenses["z_score"] = (expenses["amount"] - expenses["cat_mean"]) / expenses["cat_std"]

        # ── Combine results ──
        for idx, (_, row) in enumerate(expenses.iterrows()):
            is_iso_anomaly = iso_predictions[idx] == -1
            is_zscore_anomaly = abs(row["z_score"]) > 2.5
            is_anomaly = is_iso_anomaly or is_zscore_anomaly

            reason = ""
            if is_anomaly:
                reasons = []
                if is_zscore_anomaly and row["z_score"] > 0:
                    multiplier = round(row["amount"] / row["cat_mean"], 1)
                    reasons.append(
                        f"{multiplier}x higher than your usual {row['category']} spend"
                    )
                if row["merchant_freq"] <= 1:
                    reasons.append(f"Rare merchant with only {int(row['merchant_freq'])} transaction(s)")
                if row["is_weekend"] and row["amount"] > expenses["amount"].quantile(0.9):
                    reasons.append("Unusually large weekend transaction")
                if row["amount"] > expenses["amount"].quantile(0.95):
                    reasons.append(f"In the top 5% of your spending (₹{row['amount']:,.0f})")

                if not reasons and is_iso_anomaly:
                    reasons.append("Unusual spending pattern detected by AI")

                reason = "; ".join(reasons)

            results.append({
                "transaction_id": int(row["id"]),
                "is_anomaly": is_anomaly,
                "reason": reason if is_anomaly else "",
            })

        return results


# Singleton instance
anomaly_detector = AnomalyDetector()

