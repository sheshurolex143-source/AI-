"""Spending forecaster using weighted moving average + linear trend."""

from typing import List, Dict, Any

import numpy as np
import pandas as pd


class SpendingForecaster:
    """Forecasts future spending per category."""

    def forecast(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate spending forecasts for the next month.

        Args:
            transactions_df: DataFrame with columns: amount, category, date, type

        Returns:
            Dict with per-category forecasts and totals.
        """
        if transactions_df.empty:
            return {"forecasts": [], "total_predicted": 0, "total_confidence_low": 0, "total_confidence_high": 0}

        expenses = transactions_df[transactions_df["type"] == "expense"].copy()
        if expenses.empty:
            return {"forecasts": [], "total_predicted": 0, "total_confidence_low": 0, "total_confidence_high": 0}

        expenses["date"] = pd.to_datetime(expenses["date"])
        expenses["month"] = expenses["date"].dt.to_period("M")

        # Get monthly spending per category
        monthly = expenses.groupby(["month", "category"])["amount"].sum().reset_index()
        monthly["month_str"] = monthly["month"].astype(str)

        # Get all months in the data
        all_months = sorted(expenses["month"].unique())
        if len(all_months) < 2:
            # Not enough data for trend, just use average
            cat_avg = expenses.groupby("category")["amount"].mean()
            forecasts = []
            for cat, avg in cat_avg.items():
                forecasts.append({
                    "category": cat,
                    "current_month_avg": round(float(avg), 2),
                    "predicted_next_month": round(float(avg), 2),
                    "confidence_low": round(float(avg * 0.7), 2),
                    "confidence_high": round(float(avg * 1.3), 2),
                    "trend": "stable",
                })
            total = sum(f["predicted_next_month"] for f in forecasts)
            return {
                "forecasts": forecasts,
                "total_predicted": round(total, 2),
                "total_confidence_low": round(total * 0.7, 2),
                "total_confidence_high": round(total * 1.3, 2),
            }

        categories = monthly["category"].unique()
        forecasts = []

        for cat in categories:
            cat_data = monthly[monthly["category"] == cat].sort_values("month")

            # Create a complete monthly series (fill missing months with 0)
            month_amounts = []
            for m in all_months:
                row = cat_data[cat_data["month"] == m]
                if not row.empty:
                    month_amounts.append(float(row["amount"].values[0]))
                else:
                    month_amounts.append(0.0)

            amounts = np.array(month_amounts)
            n = len(amounts)

            # Weighted moving average (exponential-like weights, recent months matter more)
            weights = np.array([0.5 ** (n - 1 - i) for i in range(n)])
            weights = weights / weights.sum()
            wma = np.sum(amounts * weights)

            # Linear trend
            x = np.arange(n)
            if n >= 2 and np.std(amounts) > 0:
                slope, intercept = np.polyfit(x, amounts, 1)
                trend_value = slope * n  # predicted next point
                trend_component = max(0, intercept + slope * n)
            else:
                slope = 0
                trend_component = wma

            # Combine: 60% weighted MA + 40% trend
            predicted = 0.6 * wma + 0.4 * trend_component
            predicted = max(0, predicted)

            # Confidence band from residual std
            if n >= 3:
                fitted = intercept + slope * x
                residuals = amounts - fitted
                residual_std = max(np.std(residuals), predicted * 0.1)
            else:
                residual_std = predicted * 0.2

            confidence_low = max(0, predicted - 1.5 * residual_std)
            confidence_high = predicted + 1.5 * residual_std

            # Determine trend direction
            if n >= 2:
                recent_change = (amounts[-1] - amounts[-2]) / max(amounts[-2], 1) * 100
                if recent_change > 10:
                    trend = "increasing"
                elif recent_change < -10:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"

            # Current month average
            current_avg = float(amounts[-1]) if n > 0 else 0

            forecasts.append({
                "category": cat,
                "current_month_avg": round(current_avg, 2),
                "predicted_next_month": round(float(predicted), 2),
                "confidence_low": round(float(confidence_low), 2),
                "confidence_high": round(float(confidence_high), 2),
                "trend": trend,
            })

        # Sort by predicted amount descending
        forecasts.sort(key=lambda x: x["predicted_next_month"], reverse=True)

        total_predicted = sum(f["predicted_next_month"] for f in forecasts)
        total_low = sum(f["confidence_low"] for f in forecasts)
        total_high = sum(f["confidence_high"] for f in forecasts)

        return {
            "forecasts": forecasts,
            "total_predicted": round(total_predicted, 2),
            "total_confidence_low": round(total_low, 2),
            "total_confidence_high": round(total_high, 2),
        }


# Singleton instance
forecaster = SpendingForecaster()

