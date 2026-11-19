"""Transactions router handling CRUD, filtering, CSV import/export, and auto-categorization."""

import io
from datetime import date
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.database import get_db
from app.models import User, Transaction
from app.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    CSVImportResponse,
)
from app.auth import get_current_user
from app.ml.categorizer import categorizer

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = Query("date", pattern="^(date|amount|category|description)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    needs_review: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve filtered, searched, and paginated transactions."""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category and category != "All":
        query = query.filter(Transaction.category == category)
    if type and type != "All":
        query = query.filter(Transaction.type == type)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(Transaction.description.ilike(search_pattern))
    if needs_review is True:
        query = query.filter(Transaction.category_confidence < 0.60)

    total = query.count()

    # Sorting
    sort_col = getattr(Transaction, sort_by, Transaction.date)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_col))

    # Pagination
    offset = (page - 1) * per_page
    txns = query.offset(offset).limit(per_page).all()

    return {
        "transactions": txns,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    txn_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction and auto-categorize with ML if category is missing or Other."""
    category = txn_data.category
    confidence = 1.0

    if not category or category == "Other":
        prediction = categorizer.predict(txn_data.description)
        category = prediction["category"]
        confidence = prediction["confidence"]

    new_txn = Transaction(
        user_id=current_user.id,
        date=txn_data.date,
        description=txn_data.description.strip(),
        amount=txn_data.amount,
        type=txn_data.type,
        category=category,
        category_confidence=confidence,
        is_user_corrected=False,
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn


@router.get("/{txn_id}", response_model=TransactionResponse)
def get_transaction(
    txn_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch single transaction by ID."""
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return txn


@router.put("/{txn_id}", response_model=TransactionResponse)
def update_transaction(
    txn_id: int,
    update_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update transaction fields. If category changes, mark as user corrected."""
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if update_data.date is not None:
        txn.date = update_data.date
    if update_data.description is not None:
        txn.description = update_data.description.strip()
    if update_data.amount is not None:
        txn.amount = update_data.amount
    if update_data.type is not None:
        txn.type = update_data.type
    if update_data.category is not None:
        if txn.category != update_data.category:
            txn.category = update_data.category
            txn.is_user_corrected = True
            txn.category_confidence = 1.0

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    txn_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction."""
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    db.delete(txn)
    db.commit()
    return None


@router.post("/import", response_model=CSVImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Import transactions from CSV with validation and ML auto-categorization."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Normalize column headers
    df.columns = [c.strip().lower() for c in df.columns]
    required = ["date", "description", "amount", "type"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required CSV columns: {', '.join(missing)}. Required: date, description, amount, type"
        )

    successful = 0
    failed = 0
    errors = []
    new_txns = []

    for idx, row in df.iterrows():
        row_num = idx + 2
        row_errors = []

        # Validate date
        try:
            parsed_date = pd.to_datetime(row["date"]).date()
        except Exception:
            row_errors.append("Invalid date format. Expected YYYY-MM-DD.")
            parsed_date = None

        # Validate description
        desc_val = str(row["description"]).strip() if pd.notna(row["description"]) else ""
        if not desc_val:
            row_errors.append("Description cannot be empty.")

        # Validate amount
        try:
            amt_val = float(row["amount"])
            if amt_val <= 0:
                row_errors.append("Amount must be greater than zero.")
        except Exception:
            row_errors.append("Amount must be a numeric value.")
            amt_val = 0.0

        # Validate type
        type_val = str(row["type"]).strip().lower() if pd.notna(row["type"]) else ""
        if type_val not in ["income", "expense"]:
            row_errors.append("Type must be either 'income' or 'expense'.")

        if row_errors:
            failed += 1
            errors.append({"row": row_num, "errors": row_errors})
            continue

        # Category prediction if missing
        cat_val = str(row["category"]).strip() if "category" in df.columns and pd.notna(row["category"]) else None
        confidence = 1.0
        if not cat_val or cat_val.lower() == "nan":
            pred = categorizer.predict(desc_val)
            cat_val = pred["category"]
            confidence = pred["confidence"]

        txn = Transaction(
            user_id=current_user.id,
            date=parsed_date,
            description=desc_val,
            amount=amt_val,
            type=type_val,
            category=cat_val,
            category_confidence=confidence,
            is_user_corrected=False,
        )
        new_txns.append(txn)
        successful += 1

    if new_txns:
        db.bulk_save_objects(new_txns)
        db.commit()

    return {
        "total_rows": len(df),
        "successful": successful,
        "failed": failed,
        "errors": errors,
    }


@router.get("/export")
def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export all user transactions to a downloadable CSV."""
    txns = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(desc(Transaction.date)).all()

    data = [{
        "date": t.date.isoformat(),
        "description": t.description,
        "amount": t.amount,
        "type": t.type,
        "category": t.category,
        "category_confidence": t.category_confidence,
        "is_user_corrected": t.is_user_corrected,
        "is_anomaly": t.is_anomaly,
        "anomaly_reason": t.anomaly_reason or "",
    } for t in txns]

    df = pd.DataFrame(data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )
