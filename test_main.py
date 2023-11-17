from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
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


def test_register_duplicate():
    payload_duplicate = {
        "username": "testuser",
        "password": "AnotherPassword456.",
        "email": "test@example.com"
    }
    response_duplicate = client.post("/api/v1/register", json=payload_duplicate)
    assert response_duplicate.status_code == 400
    assert response_duplicate.json() == {"detail": "User already exists"}


def test_login():
    payload = {
        "username": "testuser",
        "password": "Testpassword123."
    }
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_fail():
    payload = {
        "username": "notuser",
        "password": "User1234."
    }
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_wrong_pass():
    payload = {
        "username": "testuser",
        "password": "WrongPassword456."
    }
    response = client.post("/api/v1/login", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}
    

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


def test_create_short_url_invalid_url():
    payload = {
        "original_url": "invalid_url"
    }
    response = client.post("/api/v1/shorten", json=payload)
    assert response.status_code == 422
    assert response.json() == {"detail": [{"type": "url_parsing","loc": ["body","original_url"],"msg": "Input should be a valid URL, relative URL without a base","input": "invalid_url","ctx": {"error": "relative URL without a base"},"url": "https://errors.pydantic.dev/2.5/v/url_parsing"}]}


def test_get_user_links():
    response = client.get("/api/v1/links", headers=get_user_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_links():
    response = client.get("/api/v1/links")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_redirect_original_url():
    payload = {
        "original_url": "http://example.com/"
    }
    response = client.post("/api/v1/shorten", json=payload)
    short_id = response.json()["short_id"]

    response = client.get(f"/{short_id}")
    assert response.status_code == 200
    assert response.url == "http://example.com/"


def test_redirect_original_url_not_found():
    response = client.get("/nonexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}