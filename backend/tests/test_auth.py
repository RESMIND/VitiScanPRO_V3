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
