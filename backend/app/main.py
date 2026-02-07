from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from app.core import config
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes.auth import router as auth_router
from app.routes.establishments import router as establishments_router
from app.routes.parcels import router as parcels_router
from app.routes.crops import router as crops_router
from app.routes.scans import router as scans_router
from app.routes.beta_requests import router as beta_router
from app.routes.health import router as health_router
from app.routes.authz import router as authz_router
from app.routes.audit import router as audit_router
from app.routes.admin_global import router as admin_global_router
from app.routes.billing import router as billing_router
from app.routes.password_reset import router as password_reset_router
from app.routes.ephy import router as ephy_router
from app.routes.invitations import router as invitations_router
from app.routes.trash import router as trash_router
from app.routes.costs import router as costs_router
from app.routes.onboarding import router as onboarding_router
from app.core.logger import logger
from app.core.middleware import LoggingMiddleware
from app.core.tenancy import tenant_middleware

limiter_storage_uri = config.RATE_LIMIT_REDIS_URL if getattr(config, 'RATE_LIMIT_REDIS_URL', None) and config.ENV == "production" else "memory://"
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage_uri)

app = FastAPI(
    title="VitiScan PRO V3",
    description="Agricultural management system with vineyard scanning capabilities",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.state.limiter = limiter
# app.add_middleware(LoggingMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.middleware("http")(tenant_middleware)

# V3.1 Fix: HTTPS Enforcement in production
if config.ENV == "production" and config.FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("HTTPS redirect middleware enabled")

# V3.1 Fix: Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # HSTS header for HTTPS enforcement
    if config.ENV == "production":
        response.headers["Strict-Transport-Security"] = f"max-age={config.HSTS_MAX_AGE}; includeSubDomains"
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# V3.3 Fix: CORS Middleware with strict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # Now uses env var, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(establishments_router, tags=["Establishments"])
app.include_router(parcels_router, tags=["Parcels"])
app.include_router(crops_router, tags=["Crops"])
app.include_router(scans_router, tags=["Scans"])
app.include_router(beta_router, tags=["Beta Requests"])
app.include_router(health_router)
app.include_router(authz_router)
app.include_router(audit_router)
app.include_router(admin_global_router)
app.include_router(billing_router)
app.include_router(password_reset_router)
app.include_router(ephy_router)
app.include_router(invitations_router)
app.include_router(trash_router)
app.include_router(costs_router)
app.include_router(onboarding_router, prefix="/onboarding", tags=["Onboarding"])
from app.routes.establishment_logo import router as establishment_logo_router
app.include_router(establishment_logo_router, tags=["Establishment Logo"])

@app.get("/", tags=["Health"])
def read_root():
    logger.info("Health check endpoint accessed")
    return {"message": "VitiScan v3 backend is live!", "version": "3.0.0"}

@app.on_event("startup")
async def startup_event():
    logger.info("VitiScan v3 API starting up...")
    from app.core.database import db
    # Create indexes
    try:
        await db["parcels"].create_index([("user_id", 1), ("establishment_id", 1)])
        await db["crops"].create_index([("user_id", 1), ("parcel_id", 1)])
        await db["scans"].create_index([("user_id", 1), ("parcel_id", 1)])
        await db["establishments"].create_index([("user_id", 1)])
        await db["cost_entries"].create_index([("establishment_id", 1), ("crop_type", 1), ("date", 1)])
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

