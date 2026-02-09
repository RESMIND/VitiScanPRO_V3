from fastapi import APIRouter, HTTPException, Depends, Header, Request, Form
from pydantic import BaseModel
from app.core.database import db
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, ENV, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_SECRET_KEY
from app.core.security import get_current_user, get_current_admin_user
from app.core.notifications import sms_notifier
from jose import jwt, JWTError
import datetime
from datetime import timedelta
import bcrypt
import re
import random
import string
from typing import Optional
from bson import ObjectId
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.core.utils import normalize_username, is_valid_username, is_reserved_username

router = APIRouter()
from app.core import config
limiter_storage_uri = config.RATE_LIMIT_REDIS_URL if getattr(config, 'RATE_LIMIT_REDIS_URL', None) and config.ENV == "production" else "memory://"
limiter = Limiter(key_func=get_remote_address, storage_uri=limiter_storage_uri)
logger = logging.getLogger(__name__)

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM

PHONE_REGEX = re.compile(r"^\+33[1-7][0-9]{8}$")

def normalize_phone(raw_phone: str) -> str:
    """Normalize various input formats to canonical +33XXXXXXXXX format.

    Examples accepted as input: "06 12 34 56 78", "0033 6 12 34 56 78", "+33 6 12 34 56 78".
    Output will be "+33612345678".
    """
    cleaned = re.sub(r"[\s\.\-\(\)]", "", raw_phone or "")
    cleaned = cleaned.strip()

    # Convert leading international prefix 00xx -> +xx
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    # Convert national format starting with 0 (e.g., 0612345678) to +33XXXXXXXXX
    if re.match(r"^0[1-9][0-9]{8}$", cleaned):
        cleaned = "+33" + cleaned[1:]

    return cleaned

def is_valid_phone(raw_phone: str) -> bool:
    # Validation expects the canonical +33... format
    return bool(PHONE_REGEX.match(raw_phone or ""))

# Pydantic Models
class RegisterData(BaseModel):
    phone: str | None = None
    username: str | None = None
    email: str | None = None
    password: str
    language: str
    role: str
    full_name: str | None = None
    company_name: str | None = None
    accept_terms: bool  # V2.1 FIX: GDPR consent for Terms of Service
    accept_privacy: bool  # V2.1 FIX: GDPR consent for Privacy Policy
    marketing_consent: bool = False  # Optional marketing consent

class LoginData(BaseModel):
    phone: str | None = None
    username: str | None = None
    password: str

class RefreshTokenData(BaseModel):
    refresh_token: str

class RegisterResponse(BaseModel):
    message: str
    user_id: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class MeResponse(BaseModel):
    id: str
    username: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    language: Optional[str] = None

# Phone Verification Models
class SendVerificationCodeRequest(BaseModel):
    phone: str

class SendVerificationCodeResponse(BaseModel):
    message: str
    expires_in: int  # seconds

class VerifyPhoneCodeRequest(BaseModel):
    phone: str
    code: str

class VerifyPhoneCodeResponse(BaseModel):
    message: str
    verified: bool

# In-memory storage for verification codes (use Redis in production)
verification_codes = {}

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def store_verification_code(phone: str, code: str, expires_in_seconds: int = 600):
    """Store verification code with expiration"""
    verification_codes[phone] = {
        'code': code,
        'expires_at': datetime.datetime.utcnow() + timedelta(seconds=expires_in_seconds),
        'attempts': 0
    }

def get_verification_code(phone: str) -> Optional[dict]:
    """Get verification code data if valid"""
    data = verification_codes.get(phone)
    if not data:
        return None
    
    if datetime.datetime.utcnow() > data['expires_at']:
        del verification_codes[phone]
        return None
    
    return data

def increment_verification_attempts(phone: str) -> bool:
    """Increment attempts and return True if should block"""
    data = verification_codes.get(phone)
    if not data:
        return False
    
    data['attempts'] += 1
    return data['attempts'] >= 3  # Block after 3 attempts

# Route POST /register
@router.post(
    "/register",
    summary="Înregistrare utilizator",
    description="Creează un cont nou cu username, parolă, limbă și rol",
    response_model=RegisterResponse,
    responses={
        201: {"description": "Utilizator creat"},
        400: {"description": "Username existent sau consimțământ lipsă"},
        429: {"description": "Prea multe cereri"}
    },
    status_code=201
)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterData):
    # Determine registration identity: explicit username/email or phone
    phone = None
    username_value = None

    if data.username:
        if '@' in data.username:
            # Email provided
            username_value = data.username.strip().lower()
        else:
            # Could be a phone or a chosen username
            possible_phone = normalize_phone(data.username.strip())
            if is_valid_phone(possible_phone):
                phone = possible_phone
                username_value = phone
            else:
                normalized_un = normalize_username(data.username)
                if not is_valid_username(normalized_un):
                    raise HTTPException(status_code=400, detail="Invalid username format")
                if is_reserved_username(normalized_un):
                    raise HTTPException(status_code=400, detail="Username is reserved")
                username_value = normalized_un
    elif data.phone:
        phone = normalize_phone(data.phone)
        if not is_valid_phone(phone):
            raise HTTPException(status_code=400, detail="Invalid phone format")
        # Legacy behavior: when only phone provided, use it as username for login convenience
        username_value = phone
    else:
        raise HTTPException(status_code=400, detail="Phone number or username is required")

    # Normalize username_value to lowercase for email cases
    if username_value and '@' in username_value:
        username_value = username_value.lower()

    logger.info("Registration attempt")
    
    # V2.1 FIX: Validate GDPR consent
    if not data.accept_terms or not data.accept_privacy:
        raise HTTPException(
            status_code=400, 
            detail="You must accept the Terms of Service and Privacy Policy to register"
        )
    
    # Check if user already exists (by phone or username/email)
    if phone:
        existing_user = await db["users"].find_one({
            "$or": [
                {"phone": phone},
                {"username": phone}
            ]
        })
    else:
        # Case-insensitive username uniqueness (regex with i flag) and email
        existing_user = await db["users"].find_one({
            "$or": [
                {"username": {"$regex": f'^{re.escape(username_value)}$', "$options": "i"}},
                {"email": username_value}
            ]
        })

    if existing_user:
        logger.warning("Registration failed: user already exists")
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password with bcrypt
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    user = {
        "username": username_value,
        "phone": phone,
        "email": data.email.lower() if data.email else None,
        "full_name": data.full_name,
        "company_name": data.company_name if data.company_name else None,
        "password": hashed_password.decode('utf-8'),
        "role": data.role,
        "language": data.language,
        "created_at": datetime.datetime.utcnow()
    }

    # Save to MongoDB
    result = await db["users"].insert_one(user)
    logger.info(f"User registered successfully: {phone} (ID: {result.inserted_id})")
    
    # V2.1 FIX: Log GDPR consent
    consent_log = {
        "user_id": str(result.inserted_id),
        "username": phone,
        "timestamp": datetime.datetime.utcnow(),
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "terms_accepted": data.accept_terms,
        "privacy_accepted": data.accept_privacy,
        "marketing_consent": data.marketing_consent
    }
    await db["consent_logs"].insert_one(consent_log)
    logger.info(f"GDPR consent logged for user {phone}")
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }

# Route POST /send-verification-code
@router.post(
    "/send-verification-code",
    summary="Trimite cod verificare SMS",
    description="Trimite un cod de verificare pe SMS pentru validarea numărului de telefon",
    response_model=SendVerificationCodeResponse,
    responses={
        200: {"description": "Cod trimis cu succes"},
        400: {"description": "Număr de telefon invalid"},
        429: {"description": "Prea multe cereri"}
    }
)
@limiter.limit("3/minute")
async def send_verification_code(request: Request, data: SendVerificationCodeRequest):
    phone = normalize_phone(data.phone)
    if not is_valid_phone(phone):
        raise HTTPException(status_code=400, detail="Invalid phone format")
    
    # Check if we already sent a code recently (rate limiting)
    existing_code = get_verification_code(phone)
    if existing_code:
        time_since_sent = (datetime.datetime.utcnow() - (existing_code['expires_at'] - timedelta(seconds=600))).seconds
        if time_since_sent < 60:  # Don't allow sending again within 1 minute
            raise HTTPException(status_code=429, detail="Please wait before requesting another code")
    
    # Generate and store verification code
    code = generate_verification_code()
    store_verification_code(phone, code)
    
    # Send SMS
    success = sms_notifier.send_verification_code(phone, code)
    if not success:
        logger.error(f"Failed to send verification SMS to {phone}")
        # In non-production environments, do not fail the request; allow tests/dev to proceed
        if ENV != "production":
            logger.warning("Continuing despite SMS send failure because ENV != production")
            return {"message": "Verification code generated (not sent in dev)", "expires_in": 600}
        raise HTTPException(status_code=500, detail="Failed to send verification code")
    
    logger.info(f"Verification code sent to {phone}")
    return {
        "message": "Verification code sent successfully",
        "expires_in": 600  # 10 minutes
    }

# Route POST /verify-phone-code
@router.post(
    "/verify-phone-code",
    summary="Verifică cod SMS",
    description="Verifică codul de verificare primit pe SMS",
    response_model=VerifyPhoneCodeResponse,
    responses={
        200: {"description": "Cod verificat cu succes"},
        400: {"description": "Cod invalid sau expirat"},
        429: {"description": "Prea multe încercări"}
    }
)
@limiter.limit("10/minute")
async def verify_phone_code(request: Request, data: VerifyPhoneCodeRequest):
    phone = normalize_phone(data.phone)
    if not is_valid_phone(phone):
        raise HTTPException(status_code=400, detail="Invalid phone format")
    
    # Get stored verification data
    stored_data = get_verification_code(phone)
    if not stored_data:
        raise HTTPException(status_code=400, detail="No verification code found or expired")
    
    # Check attempts
    if increment_verification_attempts(phone):
        logger.warning(f"Too many verification attempts for {phone}")
        raise HTTPException(status_code=429, detail="Too many failed attempts. Please request a new code.")
    
    # Verify code
    if stored_data['code'] != data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

# Development helper: retrieve the verification code (only allowed in non-production)
@router.get("/dev/verification-code")
async def get_dev_verification_code(phone: str):
    from app.core import config
    if config.ENV == "production":
        raise HTTPException(status_code=404, detail="Not available in production")
    code_data = get_verification_code(phone)
    if not code_data:
        raise HTTPException(status_code=404, detail="Code not found")
    return {"phone": phone, "code": code_data["code"]}    
    # Code is valid - remove it from storage
    del verification_codes[phone]

    # Update user document - set phone_verified flag
    from app.core.database import db
    user = await db["users"].find_one({"$or": [{"phone": phone}, {"username": phone}]})
    if user:
        await db["users"].update_one({"_id": user["_id"]}, {"$set": {"phone_verified": True}})

    logger.info(f"Phone verification successful for {phone}")
    return {
        "message": "Phone verified successfully",
        "verified": True
    }

@router.get("/test-simple")
async def test_simple():
    return {"message": "Simple test works"}

# Route POST /login
@router.post("/login")
async def login(request: Request, phone: str = Form(None), username: str = Form(None), password: str = Form(None)):
    # Accept form or JSON body for convenience in tests and API clients
    if not (phone or username):
        try:
            body = await request.json()
            phone = phone or body.get("phone") or body.get("username")
            password = password or body.get("password")
        except Exception:
            pass

    identifier = (phone or username or "").strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Phone number is required")

    normalized = normalize_phone(identifier)
    if is_valid_phone(normalized):
        query = {"$or": [{"phone": normalized}, {"username": normalized}]}
    else:
        # Normalize display username for matching and use case-insensitive match
        from app.core.utils import normalize_username
        normalized_username = normalize_username(identifier)
        query = {"$or": [{"username": {"$regex": f'^{re.escape(normalized_username)}$', "$options": "i"}}, {"email": identifier.lower()}]}

    try:
        # Check if user exists
        user = await db["users"].find_one(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Compare password with hash from DB
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT tokens
    access_token_expires = datetime.datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = datetime.datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token_payload = {
        "sub": str(user["_id"]),
        "role": user["role"],
        "type": "access",
        "exp": access_token_expires,
        "iat": datetime.datetime.utcnow()
    }
    
    refresh_token_payload = {
        "sub": str(user["_id"]),
        "type": "refresh",
        "exp": refresh_token_expires,
        "iat": datetime.datetime.utcnow()
    }
    
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_token_payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    # Update last login
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.datetime.utcnow(), "login_attempts": 0}}
    )
    
    return {
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "role": user["role"],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh")
async def refresh_token(request: Request, data: RefreshTokenData):
    try:
        # Decode refresh token
        payload = jwt.decode(data.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Verify user still exists
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Generate new access token
        access_payload = {
            "sub": str(user["_id"]),
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        new_access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # Generate new refresh token
        refresh_payload = {
            "sub": str(user["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }
        new_refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"Token refreshed for user {user_id}")
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# Test route for admin
@router.get("/admin-area", summary="Admin area (admin only)")
async def admin_area(user: dict = Depends(get_current_admin_user)):
    return {"msg": f"Hello, admin {user['sub']}"}

# Endpoint GET /me - returns current user profile
@router.get(
    "/me",
    summary="Profil utilizator curent",
    response_model=MeResponse,
    responses={
        200: {"description": "Profil utilizator"},
        401: {"description": "Neautorizat"}
    }
)
async def get_me(user: dict = Depends(get_current_user)):
    # Extract user_id from token (sub)
    user_id = user.get("sub")
    
    # Find user in MongoDB by _id
    try:
        db_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return user profile
    return {
        "id": str(db_user["_id"]),
        "full_name": db_user.get("full_name"),
        "username": db_user.get("username"),
        "phone": db_user.get("phone"),
        "role": db_user.get("role"),
        "language": db_user.get("language"),
        "created_at": db_user.get("created_at")
    }
