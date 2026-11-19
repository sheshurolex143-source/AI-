"""Tests for transaction CRUD, filtering, sorting, and user-correction tracking."""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_header(client):
    reg = client.post(
        "/api/auth/register",
        json={"email": "txntester@finsight.ai", "password": "Password123!", "full_name": "Txn Tester"},
    )
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


def test_transaction_crud_and_correction(client, auth_header):
    # 1. Create transaction with auto-categorization
    create_res = client.post(
        "/api/transactions",
        headers=auth_header,
        json={
            "date": "2026-11-01",
            "description": "UPI/SWIGGY*ORDER 4410",
            "amount": 450.0,
            "type": "expense",
        },
    )
    assert create_res.status_code == 201
    txn = create_res.json()
    assert txn["amount"] == 450.0
    assert txn["type"] == "expense"
    txn_id = txn["id"]

    # 2. Get single transaction
    get_res = client.get(f"/api/transactions/{txn_id}", headers=auth_header)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == txn_id

    # 3. Update category -> triggers feedback flag (is_user_corrected = True)
    update_res = client.put(
        "/api/transactions/{0}".format(txn_id),
        headers=auth_header,
        json={"category": "Groceries"},
    )
    assert update_res.status_code == 200
    updated_txn = update_res.json()
    assert updated_txn["category"] == "Groceries"
    assert updated_txn["is_user_corrected"] is True

    # 4. List transactions with filtering
    list_res = client.get(
        "/api/transactions?category=Groceries&type=expense",
        headers=auth_header,
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert any(t["id"] == txn_id for t in data["transactions"])

    # 5. Delete transaction
    del_res = client.delete(f"/api/transactions/{txn_id}", headers=auth_header)
    assert del_res.status_code == 204
