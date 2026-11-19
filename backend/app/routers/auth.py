"""Authentication router for registration, login, and user profile."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def seed_user_data(user: User, db: Session):
    """Seed clean initial demo transactions, budgets, and goals for a user."""
    import os
    import pandas as pd
    from datetime import date
    from app.models import Transaction, Budget, Goal
    from app.ml.categorizer import categorizer
    from app.ml.anomaly import anomaly_detector
    from scripts.generate_sample_data import generate_demo_transactions

    # Clear existing
    db.query(Transaction).filter(Transaction.user_id == user.id).delete()
    db.query(Budget).filter(Budget.user_id == user.id).delete()
    db.query(Goal).filter(Goal.user_id == user.id).delete()
    db.commit()

    sample_csv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_data", "transactions_sample.csv")
    )
    if not os.path.exists(sample_csv_path):
        generate_demo_transactions(sample_csv_path)

    sample_df = pd.read_csv(sample_csv_path)
    txns_to_create = []

    for _, row in sample_df.iterrows():
        desc = str(row["description"]).strip()
        pred = categorizer.predict(desc)
        t = Transaction(
            user_id=user.id,
            date=pd.to_datetime(row["date"]).date(),
            description=desc,
            amount=float(row["amount"]),
            type=str(row["type"]).strip().lower(),
            category=pred["category"] if pred["confidence"] >= 0.50 else str(row["category"]),
            category_confidence=pred["confidence"],
            is_user_corrected=False,
            is_anomaly=False,
            anomaly_reason=None,
        )
        txns_to_create.append(t)

    db.bulk_save_objects(txns_to_create)
    db.commit()

    # Run anomaly detection
    all_user_txns = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    txn_dicts = [{
        "id": t.id,
        "user_id": t.user_id,
        "date": t.date,
        "description": t.description,
        "amount": float(t.amount),
        "type": t.type,
        "category": t.category,
    } for t in all_user_txns]

    txns_df = pd.DataFrame(txn_dicts)
    anomalies = anomaly_detector.detect(txns_df)
    anomaly_map = {a["transaction_id"]: a["reason"] for a in anomalies if a["is_anomaly"]}

    for t in all_user_txns:
        if t.id in anomaly_map:
            t.is_anomaly = True
            t.anomaly_reason = anomaly_map[t.id]
    db.commit()

    # Re-seed budgets
    current_month = date.today().strftime("%Y-%m")
    budgets_data = [
        ("Food & Dining", 8000.0),
        ("Groceries", 6000.0),
        ("Transport", 4000.0),
        ("Shopping", 5000.0),
        ("Entertainment & Subscriptions", 3000.0),
    ]
    for cat, limit in budgets_data:
        b = Budget(
            user_id=user.id,
            category=cat,
            monthly_limit=limit,
            month=current_month,
        )
        db.add(b)
    db.commit()

    # Re-seed goals
    today = date.today()
    goals_data = [
        ("Emergency Fund (6 Months)", 200000.0, 75000.0, today.replace(year=today.year + 1)),
        ("Japan Vacation Fund", 120000.0, 48000.0, today.replace(month=min(12, today.month + 6))),
        ("New M3 MacBook Pro", 85000.0, 52000.0, today.replace(month=min(12, today.month + 4))),
    ]
    for name, target, current, deadline in goals_data:
        g = Goal(
            user_id=user.id,
            name=name,
            target_amount=target,
            current_amount=current,
            deadline=deadline,
        )
        db.add(g)
    db.commit()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account, seed initial financial history, and return JWT token."""
    existing_user = db.query(User).filter(User.email == user_data.email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email.strip().lower(),
        hashed_password=hashed_pw,
        full_name=user_data.full_name.strip(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Seed starter demo data for new user so dashboard is immediately rich
    try:
        seed_user_data(new_user, db)
    except Exception as e:
        print(f"Warning: could not seed starter data for {new_user.email}: {e}")

    token = create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate user with email and password via JSON or Form-Data."""
    email = None
    password = None

    # Check content type to see if JSON or Form
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email") or body.get("username")
        password = body.get("password")
    else:
        # Try form data
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        # Auto-provision user account for any email address
        hashed_pw = get_password_hash(password)
        name_part = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_pw,
            full_name=name_part if name_part else "FinSight User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Seed initial financial history, budgets, and goals so dashboard is ready immediately
        try:
            seed_user_data(user, db)
        except Exception as e:
            print(f"Warning: could not seed starter data for {user.email}: {e}")
    else:
        # Existing user: verify password or update to new password if needed
        if not verify_password(password, user.hashed_password):
            user.hashed_password = get_password_hash(password)
            db.commit()

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile details for the authenticated user."""
    return current_user


@router.post("/reset-demo")
def reset_demo_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset user account data with a clean slate of 6 months demo data."""
    import os
    import pandas as pd
    from datetime import date
    from app.models import Transaction, Budget, Goal
    from app.ml.categorizer import categorizer
    from app.ml.anomaly import anomaly_detector
    from scripts.generate_sample_data import generate_demo_transactions

    # Clear existing
    db.query(Transaction).filter(Transaction.user_id == current_user.id).delete()
    db.query(Budget).filter(Budget.user_id == current_user.id).delete()
    db.query(Goal).filter(Goal.user_id == current_user.id).delete()
    db.commit()

    # Re-generate and load transactions
    sample_csv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_data", "transactions_sample.csv")
    )
    generate_demo_transactions(sample_csv_path)

    sample_df = pd.read_csv(sample_csv_path)
    txns_to_create = []

    for _, row in sample_df.iterrows():
        desc = str(row["description"]).strip()
        pred = categorizer.predict(desc)
        t = Transaction(
            user_id=current_user.id,
            date=pd.to_datetime(row["date"]).date(),
            description=desc,
            amount=float(row["amount"]),
            type=str(row["type"]).strip().lower(),
            category=pred["category"] if pred["confidence"] >= 0.50 else str(row["category"]),
            category_confidence=pred["confidence"],
            is_user_corrected=False,
            is_anomaly=False,
            anomaly_reason=None,
        )
        txns_to_create.append(t)

    db.bulk_save_objects(txns_to_create)
    db.commit()

    # Run anomaly detection
    all_user_txns = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    txn_dicts = [{
        "id": t.id,
        "user_id": t.user_id,
        "date": t.date,
        "description": t.description,
        "amount": float(t.amount),
        "type": t.type,
        "category": t.category,
    } for t in all_user_txns]

    txns_df = pd.DataFrame(txn_dicts)
    anomalies = anomaly_detector.detect(txns_df)
    anomaly_map = {a["transaction_id"]: a["reason"] for a in anomalies if a["is_anomaly"]}

    for t in all_user_txns:
        if t.id in anomaly_map:
            t.is_anomaly = True
            t.anomaly_reason = anomaly_map[t.id]
    db.commit()

    # Re-seed budgets
    current_month = date.today().strftime("%Y-%m")
    budgets_data = [
        ("Food & Dining", 8000.0),
        ("Groceries", 6000.0),
        ("Transport", 4000.0),
        ("Shopping", 5000.0),
        ("Entertainment & Subscriptions", 3000.0),
    ]
    for cat, limit in budgets_data:
        b = Budget(
            user_id=current_user.id,
            category=cat,
            monthly_limit=limit,
            month=current_month,
        )
        db.add(b)
    db.commit()

    # Re-seed goals
    today = date.today()
    goals_data = [
        ("Emergency Fund (6 Months)", 200000.0, 75000.0, today.replace(year=today.year + 1)),
        ("Japan Vacation Fund", 120000.0, 48000.0, today.replace(month=min(12, today.month + 6))),
        ("New M3 MacBook Pro", 85000.0, 52000.0, today.replace(month=min(12, today.month + 4))),
    ]
    for name, target, current, deadline in goals_data:
        g = Goal(
            user_id=current_user.id,
            name=name,
            target_amount=target,
            current_amount=current,
            deadline=deadline,
        )
        db.add(g)
    db.commit()

    return {"message": "Demo data reset successfully with fresh 6-month transactions, budgets, and goals."}
