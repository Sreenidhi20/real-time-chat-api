import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_chat.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-1234567890")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_register_and_login_flow():
    response = client.post(
        "/register",
        json={"username": "alice", "password": "StrongPass123!"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body

    login = client.post(
        "/login",
        json={"username": "alice", "password": "StrongPass123!"},
    )

    assert login.status_code == 200, login.text
    payload = login.json()
    assert "access_token" in payload
    assert "user_id" in payload


def test_login_rejects_wrong_password():
    client.post("/register", json={"username": "bob", "password": "correct-password"})

    response = client.post(
        "/login",
        json={"username": "bob", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_users_and_messages_require_authentication():
    register_response = client.post(
        "/register",
        json={"username": "mary", "password": "StrongPass123!"},
    )
    user_id = register_response.json()["id"]

    unauth_users = client.get("/users")
    assert unauth_users.status_code == 401

    login = client.post(
        "/login",
        json={"username": "mary", "password": "StrongPass123!"},
    )
    token = login.json()["access_token"]

    users = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert users.status_code == 200
    assert all(user["id"] != user_id for user in users.json())

    messages = client.get(
        f"/messages/{user_id}/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert messages.status_code == 200
