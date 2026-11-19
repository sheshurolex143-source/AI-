"""Pydantic v2 schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# ──────────────────────── Auth ────────────────────────

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    full_name: str = Field(..., min_length=1, description="Full name")

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ──────────────────────── Transactions ────────────────────────

class TransactionCreate(BaseModel):
    date: date
    description: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category: Optional[str] = None

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    category: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    date: date
    description: str
    amount: float
    type: str
    category: str
    category_confidence: Optional[float] = None
    is_user_corrected: bool = False
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int

class CSVImportResponse(BaseModel):
    total_rows: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]


# ──────────────────────── ML ────────────────────────

class CategorizationRequest(BaseModel):
    description: str = Field(..., min_length=1)

class CategoryAlternative(BaseModel):
    category: str
    confidence: float

class CategorizationResponse(BaseModel):
    category: str
    confidence: float
    alternatives: List[CategoryAlternative]
    needs_review: bool

class RetrainResponse(BaseModel):
    message: str
    old_accuracy: Optional[float] = None
    new_accuracy: float
    samples_used: int

class ModelMetrics(BaseModel):
    accuracy: float
    per_class_metrics: Dict[str, Any]
    confusion_matrix: List[List[int]]
    feature_count: int
    training_samples: int
    trained_at: Optional[str] = None
    categories: List[str] = []


# ──────────────────────── Analytics ────────────────────────

class MonthlySummary(BaseModel):
    month: str
    income: float
    expenses: float
    savings: float
    savings_rate: float

class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int

class RecurringPayment(BaseModel):
    merchant: str
    category: str
    avg_amount: float
    frequency: str
    monthly_cost: float
    yearly_cost: float
    transaction_count: int

class AnomalyResponse(BaseModel):
    transaction: TransactionResponse
    reason: str

class ForecastItem(BaseModel):
    category: str
    current_month_avg: float
    predicted_next_month: float
    confidence_low: float
    confidence_high: float
    trend: str  # "increasing", "decreasing", "stable"

class ForecastResponse(BaseModel):
    forecasts: List[ForecastItem]
    total_predicted: float
    total_confidence_low: float
    total_confidence_high: float

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    total_savings: float
    savings_rate: float
    transaction_count: int
    top_category: str
    month_over_month_change: float
    avg_daily_expense: float
    currency_symbol: str = "₹"


# ──────────────────────── Budgets ────────────────────────

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float = Field(..., gt=0)
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")

class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = Field(None, gt=0)
    month: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    monthly_limit: float
    month: str
    spent: float = 0.0
    remaining: float = 0.0
    percentage: float = 0.0
    is_over_budget: bool = False
    projected_end_of_month: float = 0.0
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ──────────────────────── Goals ────────────────────────

class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1)
    target_amount: float = Field(..., gt=0)
    deadline: date
    current_amount: Optional[float] = Field(0.0, ge=0)

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    deadline: Optional[date] = None
    current_amount: Optional[float] = Field(None, ge=0)

class GoalResponse(BaseModel):
    id: int
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: date
    progress_percentage: float = 0.0
    remaining_amount: float = 0.0
    monthly_saving_needed: float = 0.0
    is_on_track: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ──────────────────────── Insights ────────────────────────

class Recommendation(BaseModel):
    title: str
    reason: str
    evidence: str
    estimated_saving: float
    priority: str  # "high", "medium", "low"
    category: str

class HealthScoreBreakdown(BaseModel):
    savings_rate: float
    budget_adherence: float
    debt_ratio: float
    spending_stability: float
    emergency_fund: float

class HealthScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    breakdown: HealthScoreBreakdown
    grade: str
    tips: List[str]

class WhatIfRequest(BaseModel):
    adjustments: Dict[str, float]  # category -> percentage reduction (0-100)

class WhatIfCategoryImpact(BaseModel):
    category: str
    current_spend: float
    reduction_percent: float
    new_spend: float
    saving: float

class WhatIfResponse(BaseModel):
    current_monthly_spend: float
    projected_monthly_spend: float
    monthly_savings: float
    yearly_savings: float
    new_health_score: int
    category_impact: List[WhatIfCategoryImpact]

