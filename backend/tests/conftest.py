"""
Test configuration and fixtures
"""
import os
import asyncio
from pathlib import Path
import sys
import pytest
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("MONGO_DB_NAME", "vitiscan_v3_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("REFRESH_SECRET_KEY", "test-refresh-secret")
os.environ.setdefault("EPHY_STORAGE_PATH", "data/ephy-test/ephy.sqlite")

from app.main import app
from app.core import config
import app.core.database as database_module
import app.routes.auth as auth_routes
import app.routes.establishments as establishments_routes
import app.routes.parcels as parcels_routes
import app.routes.crops as crops_routes
import app.routes.scans as scans_routes
import app.routes.beta_requests as beta_routes
import app.routes.health as health_routes
import app.routes.authz as authz_routes
import app.routes.audit as audit_routes
import app.routes.admin_global as admin_global_routes
import app.routes.billing as billing_routes
import app.routes.ephy as ephy_routes
import app.routes.onboarding as onboarding_routes
import app.core.authz_decorators as authz_decorators
import app.core.capability_tokens as capability_tokens

@pytest.fixture(autouse=True)
async def patch_test_db():
    """Bind a fresh Motor client to the running loop and reset the DB."""
    loop = asyncio.get_running_loop()
    database_module.client = AsyncIOMotorClient(config.MONGODB_URL, io_loop=loop)
    database_module.db = database_module.client[config.MONGODB_DB_NAME]

    for module in [
        auth_routes,
        establishments_routes,
        parcels_routes,
        crops_routes,
        scans_routes,
        beta_routes,
        health_routes,
        authz_routes,
        audit_routes,
        admin_global_routes,
        billing_routes,
        ephy_routes,
        onboarding_routes,
        authz_decorators,
        capability_tokens,
    ]:
        module.db = database_module.db

    auth_routes.limiter.enabled = False

    await database_module.client.drop_database(config.MONGODB_DB_NAME)
    yield
    await database_module.client.drop_database(config.MONGODB_DB_NAME)
    database_module.client.close()

@pytest.fixture
async def client():
    """Create test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_db():
    """Create test database connection"""
    test_client = AsyncIOMotorClient(config.MONGODB_URL)
    test_db = test_client[f"{config.MONGODB_DB_NAME}_test"]
    yield test_db
    # Cleanup
    await test_db.client.drop_database(f"{config.MONGODB_DB_NAME}_test")

@pytest.fixture
async def test_user():
    """Create test user"""
    return {
        "username": "test-ci@vitiscan.dev",
        "password": "Test123!@#",
        "language": "ro",
        "role": "user",
        "accept_terms": True,
        "accept_privacy": True,
        "marketing_consent": False,
        # Pre-mark phone verified for CI tests that require verified users
        "phone": "+40700123456",
        "phone_verified": True,
    }

@pytest.fixture
async def admin_user():
    """Create admin user"""
    return {
        "username": "admin@vitiscan.com",
        "password": "Admin123!@#",
        "language": "ro",
        "role": "admin",
        "accept_terms": True,
        "accept_privacy": True,
        "marketing_consent": False
    }

@pytest.fixture
async def auth_header(client, test_user):
    """Get authentication header for a pre-seeded test user"""
    # Register user (ignore duplicate errors if already present)
    await client.post("/register", json=test_user)

    # Ensure user's phone and phone_verified flags are set directly in DB for tests
    from app.core import database as database_module
    await database_module.db["users"].update_one({"username": test_user["username"]}, {"$set": {"phone": test_user.get("phone"), "phone_verified": test_user.get("phone_verified", False)}}, upsert=False)

    # Login
    response = await client.post("/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Backwards-compatible alias for tests that still use the plural name
@pytest.fixture
async def auth_headers(auth_header):
    return auth_header
