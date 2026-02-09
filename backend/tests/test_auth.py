"""
Tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user):
    """Test user registration"""
    response = await client.post("/register", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data or "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email"""
    # First registration
    await client.post("/register", json=test_user)
    # Second registration with same email
    response = await client.post("/register", json=test_user)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    # Register first
    await client.post("/register", json=test_user)
    # Login
    response = await client.post("/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    await client.post("/register", json=test_user)
    response = await client.post("/login", json={
        "username": test_user["username"],
        "password": "WrongPassword123"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email"""
    response = await client.post("/login", json={
        "username": "nonexistent@vitiscan.com",
        "password": "Password123"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers, test_user):
    """Test get current authenticated user"""
    response = await client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test get current user with invalid token"""
    response = await client.get("/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_username_normalization(client: AsyncClient):
    """Register with a display username and company_name and verify normalization and persistence"""
    payload = {
        "username": "Jean Pierre",
        "password": "Pass123!@#",
        "language": "ro",
        "role": "user",
        "accept_terms": True,
        "accept_privacy": True,
        "company_name": "Test Winery SRL"
    }

    response = await client.post("/register", json=payload)
    assert response.status_code == 201

    # Verify stored user
    from app.core import database as database_module
    user = await database_module.db["users"].find_one({"username": "jean-pierre"})
    assert user is not None
    assert user.get("company_name") == "Test Winery SRL"


@pytest.mark.asyncio
async def test_register_duplicate_username_case_insensitive(client: AsyncClient):
    payload1 = {
        "username": "Jean Pierre",
        "password": "Pass123!@#",
        "language": "ro",
        "role": "user",
        "accept_terms": True,
        "accept_privacy": True
    }
    response1 = await client.post("/register", json=payload1)
    assert response1.status_code == 201

    payload2 = {
        "username": "jean-pierre",
        "password": "Pass123!@#",
        "language": "ro",
        "role": "user",
        "accept_terms": True,
        "accept_privacy": True
    }
    response2 = await client.post("/register", json=payload2)
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_login_with_display_username(client: AsyncClient):
    payload = {
        "username": "Jean Login",
        "password": "Pass123!@#",
        "language": "ro",
        "role": "user",
        "accept_terms": True,
        "accept_privacy": True
    }
    # Register
    r = await client.post("/register", json=payload)
    assert r.status_code == 201

    # Login with the display username
    login_resp = await client.post("/login", json={"username": "Jean Login", "password": "Pass123!@#"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data

