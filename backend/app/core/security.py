"""
Security utilities for VitiScan v3
Password hashing, token generation, and validation
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Header, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import config

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_beta_token(email: str, expires_hours: int = 48) -> str:
    """Create a beta registration token (valid 48 hours)"""
    return create_access_token(
        data={"sub": email, "type": "beta"},
        expires_delta=timedelta(hours=expires_hours)
    )


def verify_beta_token(token: str) -> Optional[str]:
    """Verify beta token and return email"""
    payload = decode_access_token(token)
    if payload and payload.get("type") == "beta":
        return payload.get("sub")
    return None


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="En-tête d'autorisation manquant")
    
    # Extract token from header "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Schéma d'authentification invalide")
    except ValueError:
        raise HTTPException(status_code=401, detail="Format d'en-tête d'autorisation invalide")
    
    # Decode JWT
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Jeton invalide ou expiré")


async def get_current_admin_user(user: dict = Depends(get_current_user)):
    """Verify if user is admin"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    return user
