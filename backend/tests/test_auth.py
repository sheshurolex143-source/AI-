"""Tests for user authentication, JWT handling, and password hashing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite with StaticPool so all connections share the memory DB
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
def client():
    return TestClient(app)


def test_register_and_login_flow(client):
    # 1. Register
    reg_res = client.post(
        "/api/auth/register",
        json={
            "email": "testuser@finsight.ai",
            "password": "Password123!",
            "full_name": "Test User",
        },
    )
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]

    # 2. Duplicate registration fails
    dup_res = client.post(
        "/api/auth/register",
        json={
            "email": "testuser@finsight.ai",
            "password": "Password123!",
            "full_name": "Test User",
        },
    )
    assert dup_res.status_code == 400

    # 3. Login with correct credentials
    login_res = client.post(
        "/api/auth/login",
        json={"email": "testuser@finsight.ai", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Login with invalid password
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "testuser@finsight.ai", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401

    # 5. Get current profile (GET /me)
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "testuser@finsight.ai"
    assert me_res.json()["full_name"] == "Test User"
