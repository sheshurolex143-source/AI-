"""Analytics service for aggregating and analyzing financial data."""

import re
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Transaction, Budget, Goal
from app.config import settings
from app.ml.anomaly import anomaly_detector
from app.ml.forecast import forecaster


def _transactions_to_df(transactions: List[Transaction]) -> pd.DataFrame:
    """Helper to convert a list of Transaction ORM objects to a pandas DataFrame."""
    if not transactions:
        return pd.DataFrame(columns=[
            "id", "user_id", "date", "description", "amount", "type",
            "category", "category_confidence", "is_user_corrected",
            "is_anomaly", "anomaly_reason"
        ])
    data = [{
        "id": t.id,
        "user_id": t.user_id,
        "date": t.date,
        "description": t.description,
        "amount": float(t.amount),
        "type": t.type,
        "category": t.category,
        "category_confidence": t.category_confidence,
        "is_user_corrected": t.is_user_corrected,
        "is_anomaly": t.is_anomaly,
        "anomaly_reason": t.anomaly_reason,
    } for t in transactions]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_summary(db: Session, user_id: int, months: int = 6) -> Dict[str, Any]:
    """Calculate overall KPI summary."""
    cutoff_date = date.today() - timedelta(days=months * 30)
    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= cutoff_date
    ).all()

    df = _transactions_to_df(txns)
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "total_savings": 0.0,
            "savings_rate": 0.0,
            "transaction_count": 0,
            "top_category": "None",
            "month_over_month_change": 0.0,
            "avg_daily_expense": 0.0,
            "currency_symbol": settings.CURRENCY_SYMBOL,
        }

    income_total = float(df[df["type"] == "income"]["amount"].sum())
    expense_total = float(df[df["type"] == "expense"]["amount"].sum())
    savings = income_total - expense_total
    savings_rate = round((savings / income_total * 100), 2) if income_total > 0 else 0.0

    # Top expense category
    expenses_df = df[df["type"] == "expense"]
    top_cat = "None"
    if not expenses_df.empty:
        top_cat_counts = expenses_df.groupby("category")["amount"].sum()
        if not top_cat_counts.empty:
            top_cat = str(top_cat_counts.idxmax())

    # MoM change
    df["month"] = df["date"].dt.to_period("M")
    monthly_exp = df[df["type"] == "expense"].groupby("month")["amount"].sum()
    mom_change = 0.0
    if len(monthly_exp) >= 2:
        last_m = monthly_exp.iloc[-1]
        prev_m = monthly_exp.iloc[-2]
        if prev_m > 0:
            mom_change = round(((last_m - prev_m) / prev_m) * 100, 2)

    # Average daily expense over date span
    date_span_days = max(1, (df["date"].max() - df["date"].min()).days + 1)
    avg_daily = round(expense_total / date_span_days, 2)

    return {
        "total_income": round(income_total, 2),
        "total_expenses": round(expense_total, 2),
        "total_savings": round(savings, 2),
        "savings_rate": savings_rate,
        "transaction_count": len(df),
        "top_category": top_cat,
        "month_over_month_change": mom_change,
        "avg_daily_expense": avg_daily,
        "currency_symbol": settings.CURRENCY_SYMBOL,
    }


def get_monthly_breakdown(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Compute monthly income vs expense vs savings and savings rate."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    df = _transactions_to_df(txns)
    if df.empty:
        return []

    df["month"] = df["date"].dt.strftime("%Y-%m")
    months = sorted(df["month"].unique())

    result = []
    for m in months:
        m_df = df[df["month"] == m]
        inc = float(m_df[m_df["type"] == "income"]["amount"].sum())
        exp = float(m_df[m_df["type"] == "expense"]["amount"].sum())
        sav = inc - exp
        rate = round((sav / inc * 100), 2) if inc > 0 else 0.0
        result.append({
            "month": m,
            "income": round(inc, 2),
            "expenses": round(exp, 2),
            "savings": round(sav, 2),
            "savings_rate": rate,
        })
    return result


def get_category_breakdown(
    db: Session, user_id: int, month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Compute category-wise expenses and percentages."""
    query = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    )
    txns = query.all()
    df = _transactions_to_df(txns)
    if df.empty:
        return []

    if month:
        df["month"] = df["date"].dt.strftime("%Y-%m")
        df = df[df["month"] == month]
        if df.empty:
            return []

    total_expense = df["amount"].sum()
    if total_expense == 0:
        return []

    cat_grouped = df.groupby("category").agg(
        amount=("amount", "sum"),
        count=("id", "count")
    ).reset_index()

    cat_grouped["percentage"] = (cat_grouped["amount"] / total_expense * 100).round(2)
    cat_grouped = cat_grouped.sort_values(by="amount", ascending=False)

    return [{
        "category": row["category"],
        "amount": round(float(row["amount"]), 2),
        "percentage": float(row["percentage"]),
        "transaction_count": int(row["count"]),
    } for _, row in cat_grouped.iterrows()]


def detect_recurring_payments(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Group by normalized merchant with similar amounts at roughly monthly intervals."""
    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).all()
    df = _transactions_to_df(txns)
    if df.empty or len(df) < 3:
        return []

    def clean_name(desc: str) -> str:
        s = re.sub(r'(UPI|POS|NEFT|IMPS|NACH|DEBIT|CREDIT|CARD|REF|TXN|INR|\*|\/|\:)', ' ', desc.upper())
        s = re.sub(r'\b[0-9]+\b', '', s)
        tokens = [w for w in s.split() if len(w) > 2]
        return " ".join(tokens[:2]).title() if tokens else desc[:15].title()

    df["merchant"] = df["description"].apply(clean_name)
    df = df.sort_values(by=["merchant", "date"])

    recurring = []
    for merchant, group in df.groupby("merchant"):
        if len(group) < 2:
            continue

        # Check date intervals
        dates = group["date"].sort_values().tolist()
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_interval = np.mean(intervals)

        # Check amount variation (coefficient of variation <= 25%)
        amounts = group["amount"].values
        mean_amt = np.mean(amounts)
        std_amt = np.std(amounts)
        cv = (std_amt / mean_amt) if mean_amt > 0 else 1.0

        # Roughly monthly (every 22 - 38 days) or consistent amounts
        if (20 <= avg_interval <= 40 or cv < 0.15) and len(group) >= 2:
            avg_amount = float(round(mean_amt, 2))
            cat = group["category"].mode()[0] if not group["category"].empty else "Bills & Utilities"
            recurring.append({
                "merchant": merchant,
                "category": cat,
                "avg_amount": avg_amount,
                "frequency": "Monthly",
                "monthly_cost": avg_amount,
                "yearly_cost": round(avg_amount * 12, 2),
                "transaction_count": len(group),
            })

    recurring.sort(key=lambda r: r["monthly_cost"], reverse=True)
    return recurring


def get_anomalies(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Detect anomalies in the user's transactions and return them."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    df = _transactions_to_df(txns)
    if df.empty:
        return []

    anomaly_flags = anomaly_detector.detect(df)
    flag_dict = {f["transaction_id"]: f for f in anomaly_flags if f["is_anomaly"]}

    # Return matching transactions
    results = []
    for t in txns:
        if t.id in flag_dict:
            results.append({
                "transaction": {
                    "id": t.id,
                    "user_id": t.user_id,
                    "date": t.date,
                    "description": t.description,
                    "amount": t.amount,
                    "type": t.type,
                    "category": t.category,
                    "category_confidence": t.category_confidence,
                    "is_user_corrected": t.is_user_corrected,
                    "is_anomaly": True,
                    "anomaly_reason": flag_dict[t.id]["reason"],
                    "created_at": t.created_at,
                    "updated_at": t.updated_at,
                },
                "reason": flag_dict[t.id]["reason"],
            })
    return results


def get_forecast(db: Session, user_id: int) -> Dict[str, Any]:
    """Generate spending forecast for the next month."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    df = _transactions_to_df(txns)
    return forecaster.forecast(df)
