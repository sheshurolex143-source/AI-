"""Analytics router providing summaries, trends, recurring payments, anomalies, and forecasts."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    AnalyticsSummary,
    MonthlySummary,
    CategoryBreakdown,
    RecurringPayment,
    AnomalyResponse,
    ForecastResponse,
)
from app.auth import get_current_user
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Overall financial KPI summary."""
    return analytics_service.get_summary(db, current_user.id, months)


@router.get("/monthly", response_model=List[MonthlySummary])
def get_monthly(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Monthly income vs expense vs savings history."""
    return analytics_service.get_monthly_breakdown(db, current_user.id)


@router.get("/categories", response_model=List[CategoryBreakdown])
def get_categories(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Category breakdown for expenses."""
    return analytics_service.get_category_breakdown(db, current_user.id, month)


@router.get("/recurring", response_model=List[RecurringPayment])
def get_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recurring payment and subscription detection."""
    return analytics_service.detect_recurring_payments(db, current_user.id)


@router.get("/anomalies", response_model=List[AnomalyResponse])
def get_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Flagged anomaly transactions with plain-English reasons."""
    return analytics_service.get_anomalies(db, current_user.id)


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Next month spending forecast by category and in total."""
    return analytics_service.get_forecast(db, current_user.id)
