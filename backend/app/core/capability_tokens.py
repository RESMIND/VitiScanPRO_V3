"""
Capability Tokens - Temporary authorization tokens for secure sharing
Allows users to share resources with specific actions for limited time
"""
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import secrets
import hashlib
from app.core.database import db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class CapabilityToken(BaseModel):
    """Temporary token granting specific permissions"""
    token: str  # Hashed token
    issuer_id: str  # Who created the token
    subject_id: Optional[str] = None  # Who can use it (None = anyone with token)
    resource_type: str  # parcel, establishment, etc.
    resource_id: str  # Specific resource
    action: str  # view, edit, export, etc.
    created_at: datetime
    expires_at: datetime
    used_count: int = 0
    max_uses: Optional[int] = None  # None = unlimited
    metadata: dict = {}

class CapabilityTokenManager:
    """Manages capability tokens for secure sharing"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.capability_tokens
    
    async def create_token(
        self,
        issuer_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        expires_in_hours: int = 24,
        subject_id: Optional[str] = None,
        max_uses: Optional[int] = None,
        metadata: dict = {}
    ) -> str:
        """
        Create a capability token
        
        Returns: The raw token (show this to user ONCE!)
        """
        # Generate random token
        raw_token = secrets.token_urlsafe(32)
        
        # Hash token for storage (never store raw token!)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # Create token document
        token_doc = {
            "token": token_hash,
            "issuer_id": issuer_id,
            "subject_id": subject_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=expires_in_hours),
            "used_count": 0,
            "max_uses": max_uses,
            "metadata": metadata
        }
        
        await self.collection.insert_one(token_doc)
        
        # Return raw token (this is the only time user sees it!)
        return raw_token
    
    async def verify_token(
        self,
        raw_token: str,
        resource_type: str,
        resource_id: str,
        action: str,
        subject_id: Optional[str] = None
    ) -> bool:
        """
        Verify if a capability token is valid
        
        Returns: True if valid, False otherwise
        """
        # Hash the raw token
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # Find token
        token_doc = await self.collection.find_one({"token": token_hash})
        
        if not token_doc:
            return False
        
        # Check expiration
        if datetime.utcnow() > token_doc["expires_at"]:
            return False
        
        # Check resource match
        if token_doc["resource_type"] != resource_type or \
           token_doc["resource_id"] != resource_id:
            return False
        
        # Check action match
        if token_doc["action"] != action:
            return False
        
        # Check subject (if restricted)
        if token_doc["subject_id"] and token_doc["subject_id"] != subject_id:
            return False
        
        # Check max uses
        if token_doc["max_uses"] and token_doc["used_count"] >= token_doc["max_uses"]:
            return False
        
        # Increment use count
        await self.collection.update_one(
            {"token": token_hash},
            {"$inc": {"used_count": 1}}
        )
        
        return True
    
    async def revoke_token(self, raw_token: str) -> bool:
        """Revoke a capability token"""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        result = await self.collection.delete_one({"token": token_hash})
        return result.deleted_count > 0

    async def revoke_token_by_id(self, token_id: str, issuer_id: str) -> bool:
        """Revoke a capability token by MongoDB id (issuer only)"""
        try:
            oid = ObjectId(token_id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": oid, "issuer_id": issuer_id})
        return result.deleted_count > 0

    async def inspect_token(self, raw_token: str) -> Optional[dict]:
        """Return token metadata if exists (without exposing raw token)"""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_doc = await self.collection.find_one({"token": token_hash})
        if not token_doc:
            return None
        token_doc["_id"] = str(token_doc["_id"])
        token_doc.pop("token", None)
        return token_doc
    
    async def list_tokens(self, issuer_id: str) -> List[dict]:
        """List all tokens created by a user"""
        cursor = self.collection.find(
            {"issuer_id": issuer_id},
            {"token": 0}  # Don't return hashed token
        )
        return await cursor.to_list(length=None)
    
    async def cleanup_expired(self) -> int:
        """Remove expired tokens"""
        result = await self.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count


# Global instance
capability_manager = CapabilityTokenManager(db)

__all__ = ["CapabilityToken", "CapabilityTokenManager", "capability_manager"]
