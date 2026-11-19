"""ML router for inference, retraining feedback loop, and metrics inspection."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Transaction
from app.schemas import CategorizationRequest, CategorizationResponse, RetrainResponse, ModelMetrics
from app.auth import get_current_user
from app.ml.categorizer import categorizer

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/categorize", response_model=CategorizationResponse)
def categorize_description(
    req: CategorizationRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict category with confidence scores and top-3 alternatives."""
    return categorizer.predict(req.description)


@router.post("/retrain", response_model=RetrainResponse)
def retrain_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrain the classifier using synthetic data plus user-corrected transactions."""
    old_metrics = categorizer.get_metrics()
    old_acc = old_metrics.get("accuracy") if old_metrics else None

    # Fetch all user-corrected transactions across users
    corrected = db.query(Transaction).filter(
        Transaction.is_user_corrected == True
    ).all()

    user_corrections = [
        {"description": t.description, "category": t.category}
        for t in corrected
    ]

    try:
        new_metrics = categorizer.train(user_corrections=user_corrections)
        return {
            "message": "Model retrained successfully with user feedback loop.",
            "old_accuracy": old_acc,
            "new_accuracy": new_metrics["accuracy"],
            "samples_used": new_metrics["total_samples"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model retraining failed: {str(e)}"
        )


@router.get("/metrics", response_model=ModelMetrics)
def get_model_metrics(current_user: User = Depends(get_current_user)):
    """Fetch the latest model evaluation metrics and confusion matrix."""
    metrics = categorizer.get_metrics()
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found. Please train the model first."
        )
    return metrics
