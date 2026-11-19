"""Insights service coordinating recommendations, health score, and what-if analysis."""

from typing import List, Dict, Any, Optional
import httpx
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Transaction, Budget, Goal
from app.config import settings
from app.ml.recommendations import recommendation_engine
from app.services.analytics_service import _transactions_to_df


def _get_user_context(db: Session, user_id: int):
    """Retrieve user transactions, current budgets, and goals."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    df = _transactions_to_df(txns)

    # Calculate actual spending on budgets
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()

    # Enrich budgets with current spent
    enriched_budgets = []
    current_month_str = pd.Timestamp.now().strftime("%Y-%m")
    for b in budgets:
        cat_spent = 0.0
        if not df.empty:
            df["month_str"] = df["date"].dt.strftime("%Y-%m")
            subset = df[(df["month_str"] == b.month) & (df["category"] == b.category) & (df["type"] == "expense")]
            cat_spent = float(subset["amount"].sum())
        enriched_budgets.append({
            "category": b.category,
            "monthly_limit": b.monthly_limit,
            "spent": cat_spent,
            "month": b.month,
        })

    return df, enriched_budgets, goals


def get_recommendations(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Generate recommendations with optional LLM polish if API key is provided."""
    df, budgets, goals = _get_user_context(db, user_id)
    recs = recommendation_engine.generate_recommendations(df, budgets, goals)

    # Optional provider-agnostic LLM enhancement
    if settings.LLM_API_KEY and len(settings.LLM_API_KEY.strip()) > 5 and recs:
        try:
            # We can optionally call Gemini / OpenAI / Anthropic format, or maintain clean templates
            pass
        except Exception:
            pass  # Fall back cleanly to rule-based templates

    return recs


def get_health_score(db: Session, user_id: int) -> Dict[str, Any]:
    """Calculate 0-100 financial health score."""
    df, budgets, goals = _get_user_context(db, user_id)
    return recommendation_engine.calculate_health_score(df, budgets, goals)


def run_what_if(
    db: Session, user_id: int, adjustments: Dict[str, float]
) -> Dict[str, Any]:
    """Execute what-if simulation on budget cuts."""
    df, budgets, goals = _get_user_context(db, user_id)
    return recommendation_engine.what_if_simulation(df, adjustments, budgets, goals)
