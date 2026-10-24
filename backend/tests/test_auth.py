import pytest
from app.models.auth import User, UserRole
from app.core.security import verify_password

def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "creator@novusbio.com",
        "password": "demo1234"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "creator@novusbio.com"
    assert data["user"]["role"] == UserRole.CREATOR.value

def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "creator@novusbio.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_switch_demo_role(client):
    res = client.post("/api/v1/auth/switch-demo-role?role=brand_owner")
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == UserRole.BRAND_OWNER.value
