"""Goals router for savings goals tracking and deadline milestones."""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Goal
from app.schemas import GoalCreate, GoalUpdate, GoalResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/goals", tags=["Goals"])


def _calculate_goal_stats(goal: Goal) -> dict:
    """Calculate progress percentage, remaining deficit, and required monthly contribution."""
    target = max(1.0, goal.target_amount)
    current = max(0.0, goal.current_amount)
    progress_pct = round(min(100.0, (current / target) * 100), 1)
    remaining = max(0.0, target - current)

    today = date.today()
    days_left = (goal.deadline - today).days
    months_left = max(1.0, days_left / 30.4)

    monthly_needed = round(remaining / months_left, 2) if remaining > 0 else 0.0
    is_on_track = progress_pct >= 50.0 or (days_left > 0 and monthly_needed <= (target * 0.2))

    return {
        "id": goal.id,
        "user_id": goal.user_id,
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "deadline": goal.deadline,
        "progress_percentage": progress_pct,
        "remaining_amount": round(remaining, 2),
        "monthly_saving_needed": monthly_needed,
        "is_on_track": is_on_track,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
    }


@router.get("", response_model=List[GoalResponse])
def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all savings goals with calculated milestones."""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    return [_calculate_goal_stats(g) for g in goals]


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new savings goal."""
    g = Goal(
        user_id=current_user.id,
        name=data.name.strip(),
        target_amount=data.target_amount,
        current_amount=data.current_amount or 0.0,
        deadline=data.deadline,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return _calculate_goal_stats(g)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update goal attributes or deposited amount."""
    g = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found.")

    if data.name is not None:
        g.name = data.name.strip()
    if data.target_amount is not None:
        g.target_amount = data.target_amount
    if data.current_amount is not None:
        g.current_amount = data.current_amount
    if data.deadline is not None:
        g.deadline = data.deadline

    db.commit()
    db.refresh(g)
    return _calculate_goal_stats(g)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a savings goal."""
    g = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found.")

    db.delete(g)
    db.commit()
    return None
