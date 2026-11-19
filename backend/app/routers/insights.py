"""Insights router for recommendations, financial health score, and what-if simulation."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Recommendation, HealthScore, WhatIfRequest, WhatIfResponse
from app.auth import get_current_user
from app.services import insights_service

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/recommendations", response_model=List[Recommendation])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate prioritized, evidence-based financial recommendations."""
    return insights_service.get_recommendations(db, current_user.id)


@router.get("/health-score", response_model=HealthScore)
def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve 0-100 financial health score with transparent metric breakdown."""
    return insights_service.get_health_score(db, current_user.id)


@router.post("/what-if", response_model=WhatIfResponse)
def run_what_if_simulation(
    req: WhatIfRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulate spending cuts by category and calculate impact on health score & savings."""
    return insights_service.run_what_if(db, current_user.id, req.adjustments)
