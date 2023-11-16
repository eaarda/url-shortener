import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import HttpUrl


from main import app
from core.security import Auth
from core.db import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
    
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def get_user_headers():
    login_payload = {
        "username": "testuser",
        "password": "Testpassword123."
    }
    response = client.post("/api/v1/login", json=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register():
    payload = {
        "username": "testuser",
        "password": "Testpassword123.",
        "email": "test@example.com"
    }
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_login():
    payload = {
        "username": "testuser",
        "password": "Testpassword123."
    }
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_short_url_without_token():
    payload = {
        "original_url": "http://example.com"
    }
    response = client.post("/api/v1/shorten", json=payload)
    assert response.status_code == 200
    assert "short_url" in response.json()


def test_create_short_url_with_token():
    payload = {
        "original_url": "http://example.com"
    }
    response = client.post("/api/v1/shorten", json=payload, headers=get_user_headers())
    assert response.status_code == 200
    assert "short_url" in response.json()


def test_get_user_links():
    response = client.get("/api/v1/links", headers=get_user_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)
