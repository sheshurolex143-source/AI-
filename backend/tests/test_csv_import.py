"""Tests for CSV statement parser, validation, and row-level error reporting."""

import io
import pytest
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
        json={"email": "csvtester@finsight.ai", "password": "Password123!", "full_name": "CSV Tester"},
    )
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


def test_csv_import_valid_and_invalid_rows(client, auth_header):
    csv_content = (
        "date,description,amount,type,category\n"
        "2026-11-01,BIGBASKET RETAIL BLR,1450.00,expense,Groceries\n"
        "2026-11-02,SALARY CREDIT ACME,75000.00,income,Income\n"
        "INVALID-DATE,MALFORMED ROW,-500,invalid_type,\n"
        "2026-11-03,NETFLIX RECURRING,649.00,expense,\n"
    )

    files = {"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/transactions/import", headers=auth_header, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 4
    assert data["successful"] == 3
    assert data["failed"] == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0]["row"] == 4  # 1 header + row 3 data = row index 4
