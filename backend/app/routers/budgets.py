"""Budgets router for monthly spending cap tracking and overspend warnings."""

from calendar import monthrange
from datetime import datetime, date
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Budget, Transaction
from app.schemas import BudgetCreate, BudgetUpdate, BudgetResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


def _calculate_budget_stats(budget: Budget, db: Session, user_id: int) -> dict:
    """Calculate actual spend, remaining balance, and projected end of month spend."""
    year, month_num = map(int, budget.month.split("-"))
    days_in_month = monthrange(year, month_num)[1]

    # Calculate spent in this category for that month
    start_date = date(year, month_num, 1)
    end_date = date(year, month_num, days_in_month)

    spent_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense",
        Transaction.category == budget.category,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ).all()

    spent = float(sum(t.amount for t in spent_txns))
    remaining = budget.monthly_limit - spent
    percentage = round((spent / budget.monthly_limit * 100), 2) if budget.monthly_limit > 0 else 0.0
    is_over = spent > budget.monthly_limit

    # Projection based on current day of month
    today = date.today()
    if today.year == year and today.month == month_num:
        current_day = max(1, today.day)
        daily_rate = spent / current_day
        projected = round(daily_rate * days_in_month, 2)
    elif today > end_date:
        projected = spent
    else:
        projected = budget.monthly_limit

    return {
        "id": budget.id,
        "user_id": budget.user_id,
        "category": budget.category,
        "monthly_limit": budget.monthly_limit,
        "month": budget.month,
        "spent": round(spent, 2),
        "remaining": round(remaining, 2),
        "percentage": percentage,
        "is_over_budget": is_over,
        "projected_end_of_month": projected,
        "created_at": budget.created_at,
    }


@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all budgets with live spending status and projections."""
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return [_calculate_budget_stats(b, db, current_user.id) for b in budgets]


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a monthly budget for a category."""
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == data.category,
        Budget.month == data.month,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Budget for {data.category} in {data.month} already exists."
        )

    b = Budget(
        user_id=current_user.id,
        category=data.category,
        monthly_limit=data.monthly_limit,
        month=data.month,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return _calculate_budget_stats(b, db, current_user.id)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing budget."""
    b = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id,
    ).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found.")

    if data.monthly_limit is not None:
        b.monthly_limit = data.monthly_limit
    if data.month is not None:
        b.month = data.month

    db.commit()
    db.refresh(b)
    return _calculate_budget_stats(b, db, current_user.id)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a budget."""
    b = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id,
    ).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found.")

    db.delete(b)
    db.commit()
    return None
