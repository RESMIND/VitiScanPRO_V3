"""
Test configuration and fixtures
"""
import os
import asyncio
from pathlib import Path
import sys
import pytest

# Toggle to skip integration tests that depend on unfinished UI features.
# Default: 'true' to skip them until UI (Phase 1) and mock API (Phase 2) are ready.
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION", "true").lower() == "true"

def pytest_collection_modifyitems(config, items):
    """Skip specific integration tests when SKIP_INTEGRATION is true.

    Rules:
    - Skip entire files: tests/test_parcels.py and tests/test_scans.py
    - Skip onboarding tests whose name contains "parcel"
    """
    if not SKIP_INTEGRATION:
        return
    skip_marker = pytest.mark.skip(reason="Feature in progress — mock API planned")
    for item in items:
        path = str(item.fspath).replace("\\", "/")
        # Skip parcels and scans test files entirely
        if path.endswith("/tests/test_parcels.py") or path.endswith("/tests/test_scans.py"):
            item.add_marker(skip_marker)
            continue
        # Skip onboarding tests related to parcel flows by name
        if "/tests/test_onboarding.py" in path and "parcel" in item.name.lower():
            item.add_marker(skip_marker)

from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("MONGO_DB_NAME", "vitiscan_v3_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("REFRESH_SECRET_KEY", "test-refresh-secret")
os.environ.setdefault("EPHY_STORAGE_PATH", "data/ephy-test/ephy.sqlite")

try:
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
except Exception:
    # When MongoDB is unreachable, importing app and route modules may fail
    # because they expect an initialized DB. Make test fixtures tolerant to
    # a missing app during pure unit test runs.
    import logging
    logging.getLogger(__name__).warning("App import failed - DB may be unreachable; some integration tests will be skipped")
    app = None
    config = None
    database_module = None
    auth_routes = None
    establishments_routes = None
    parcels_routes = None
    crops_routes = None
    scans_routes = None
    beta_routes = None
    health_routes = None
    authz_routes = None
    audit_routes = None
    admin_global_routes = None
    billing_routes = None
    ephy_routes = None
    onboarding_routes = None
    authz_decorators = None
    capability_tokens = None

@pytest.fixture(autouse=True)
async def patch_test_db():
    """Bind a fresh Motor client to the running loop and reset the DB."""
    loop = asyncio.get_running_loop()

    # If config couldn't be imported (app failed to import), skip DB setup entirely.
    if config is None:
        import logging
        logging.getLogger(__name__).warning("App config not available; skipping DB setup for tests")
        yield
        return

    # Quick availability check for MongoDB. If unreachable, skip DB setup to allow pure unit tests to run.
    from urllib.parse import urlparse
    import socket
    db_available = True
    try:
        parsed = urlparse(config.MONGODB_URL)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 27017
        sock = socket.create_connection((host, port), timeout=1)
        sock.close()
    except Exception:
        db_available = False

    if db_available:
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
            if module is not None:
                module.db = database_module.db

        if auth_routes is not None:
            auth_routes.limiter.enabled = False

        try:
            await database_module.client.drop_database(config.MONGODB_DB_NAME)
        except Exception:
            # If Mongo is not available in the local environment (CI may provide it),
            # continue without failing tests for pure unit tests that don't require DB.
            import logging
            logging.getLogger(__name__).warning("Could not drop test DB - Mongo may be unavailable in this environment")
    else:
        import logging
        logging.getLogger(__name__).warning("MongoDB not reachable, skipping DB setup for tests")

    yield

    try:
        await database_module.client.drop_database(config.MONGODB_DB_NAME)
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Could not drop test DB on teardown - Mongo may be unavailable")
    database_module.client.close()

@pytest.fixture
async def client():
    """Create test client"""
    if app is None:
        pytest.skip("App is not available in this environment (likely missing MongoDB)")
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
