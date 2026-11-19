"""One-command seed script for FinSight AI.
1. Generates training data and sample transactions.
2. Trains the ML categorizer model.
3. Initializes SQLite database tables.
4. Creates or resets the demo user (demo@finsight.ai / Demo@123).
5. Populates 6 months of demo transactions with ML auto-categorization and anomaly detection.
6. Sets up monthly budgets and savings goals.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import date
import pandas as pd

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, SessionLocal, Base
from app.models import User, Transaction, Budget, Goal
from app.auth import get_password_hash
from app.config import settings
from app.ml.categorizer import categorizer
from app.ml.anomaly import anomaly_detector
from scripts.generate_sample_data import generate_training_data, generate_demo_transactions
from scripts.train_model import run_training


def seed_all():
    print("==================================================")
    print(">>> FinSight AI - Master Setup & Seed Script <<<")
    print("==================================================")

    # 1. Generate Datasets
    train_data_path = settings.TRAINING_DATA_PATH
    sample_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "transactions_sample.csv"))
    
    print("\n[Step 1/5] Generating synthetic data & sample transactions...")
    n_train = generate_training_data(train_data_path, samples_per_category=280)
    n_sample = generate_demo_transactions(sample_csv_path)
    print(f"  • Training corpus: {n_train} bank descriptions generated.")
    print(f"  • Demo statement:  {n_sample} realistic transactions created.")

    # 2. Train Model
    print("\n[Step 2/5] Training TF-IDF + LinearSVC text categorizer...")
    metrics = run_training()

    # 3. Initialize DB Schema
    print("\n[Step 3/5] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 4. Create Demo User
        print("\n[Step 4/5] Setting up demo user account...")
        demo_email = "demo@finsight.ai"
        user = db.query(User).filter(User.email == demo_email).first()

        if user:
            print(f"  • Existing demo user found (ID: {user.id}). Cleaning existing demo records...")
            db.query(Transaction).filter(Transaction.user_id == user.id).delete()
            db.query(Budget).filter(Budget.user_id == user.id).delete()
            db.query(Goal).filter(Goal.user_id == user.id).delete()
            db.commit()
        else:
            print("  • Creating new demo user (demo@finsight.ai / Demo@123)...")
            user = User(
                email=demo_email,
                hashed_password=get_password_hash("Demo@123"),
                full_name="Alex Morgan",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  • Demo user created with ID {user.id}.")

        # 5. Load and Categorize Transactions
        print("\n[Step 5/5] Ingesting transactions with AI categorization & anomaly detection...")
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

        # Fetch loaded transactions to run anomaly detection
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

        # Update anomaly flags in DB
        anomaly_count = 0
        for t in all_user_txns:
            if t.id in anomaly_map:
                t.is_anomaly = True
                t.anomaly_reason = anomaly_map[t.id]
                anomaly_count += 1
        db.commit()
        print(f"  • Ingested {len(all_user_txns)} transactions.")
        print(f"  • Detected and flagged {anomaly_count} spending anomalies.")

        # Seed Budgets for current month
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
        print(f"  • Seeded {len(budgets_data)} monthly budgets for {current_month}.")

        # Seed Goals
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
        print(f"  • Seeded {len(goals_data)} savings goals.")

    finally:
        db.close()

    print("\n==================================================")
    print("SUCCESS: Master setup complete! Demo account credentials:")
    print("   Email:    demo@finsight.ai")
    print("   Password: Demo@123")
    print("==================================================\n")


if __name__ == "__main__":
    seed_all()
