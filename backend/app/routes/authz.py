"""
Authorization API endpoints
Exposes authorization engine for policy checks
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from datetime import datetime
from app.core.authz_engine import authz_engine, AuthzSubject, AuthzResource, ActionType, ResourceType
from app.core.logger import logger
from app.routes.auth import get_current_user
from app.models.relationships import RelationshipManager
from app.core.database import db
from app.core.utils import validate_object_id

router = APIRouter(prefix="/authz", tags=["Authorization"])

# Initialize relationship manager
relationship_manager = RelationshipManager(db)

class AuthzCheckRequest(BaseModel):
    """Request model for authorization check"""
    subject: AuthzSubject
    action: str
    resource: AuthzResource

class AuthzCheckResponse(BaseModel):
    """Response model for authorization check"""
    outcome: str  # "allow" or "deny"
    reasons: List[str]
    matched_policies: List[str]

@router.post(
    "/check",
    response_model=AuthzCheckResponse,
    summary="Check authorization",
    description="Unified authorization check using RBAC + ABAC + ReBAC"
)
async def check_authorization(request: AuthzCheckRequest):
    """
    Check if a subject is authorized to perform an action on a resource
    
    Example request:
    ```json
    {
      "subject": {
        "id": "user:123",
        "role": "consultant",
        "attrs": {"mfa": true, "region": "PACA"}
      },
      "action": "edit",
      "resource": {
        "id": "parcel:456",
        "type": "parcel",
        "relations": {"owner": "user:123", "consultant": ["user:789"]}
      }
    }
    ```
    """
    try:
        decision = authz_engine.check(
            subject=request.subject,
            action=request.action,
            resource=request.resource
        )
        
        logger.info(
            f"Authz check: {request.subject.id} {request.action} {request.resource.id} -> {decision.outcome}"
        )
        
        return AuthzCheckResponse(
            outcome=decision.outcome,
            reasons=decision.reasons,
            matched_policies=decision.matched_policies
        )
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        raise HTTPException(status_code=500, detail="Authorization check failed")

@router.post(
    "/why",
    summary="Explain authorization decision",
    description="Get detailed explanation of why access was granted or denied. Supports dry_run for what-if scenarios.",
    include_in_schema=False
)
async def explain_authorization(
    request: AuthzCheckRequest,
    dry_run: bool = False
):
    """
    Explain why an authorization decision was made
    Useful for debugging and audit logs
    
    dry_run=true: Simulate authorization without logging (what-if analysis)
    dry_run=false: Normal operation with audit logging
    """
    try:
        explanation = authz_engine.why(
            subject=request.subject,
            action=request.action,
            resource=request.resource
        )
        
        # Add dry_run flag to response
        explanation["dry_run"] = dry_run
        
        if dry_run:
            explanation["note"] = "This is a simulation - no audit log created"
        else:
            # Log the authorization check (import from audit.py)
            from app.routes.audit import log_audit_event
            await log_audit_event(
                user_id=request.subject.id,
                action="authz_why",
                outcome=explanation["decision"],
                resource_type=request.resource.type,
                resource_id=request.resource.id,
                details={"action": request.action, "reasons": explanation.get("reasons", [])}
            )
        
        return explanation
    except Exception as e:
        logger.error(f"Authorization explanation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to explain decision")

class AddRelationshipRequest(BaseModel):
    """Request to add a relationship"""
    user_id: str
    resource_type: str
    resource_id: str
    relation_type: str  # owner, consultant, viewer, etc.
    expires_at: Optional[str] = None

@router.post(
    "/relationships",
    summary="Add resource relationship",
    description="Grant a user relationship to a resource (owner, consultant, viewer)"
)
async def add_relationship(
    request: AddRelationshipRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a relationship between user and resource
    Requires: User must be owner or admin
    """
    try:
        # Check if current user is authorized to grant relationships
        # (either admin or owner of the resource)
        if current_user.get("role") != "admin":
            # Check if user is owner
            existing_relations = await relationship_manager.get_resource_relationships(
                resource_type=request.resource_type,
                resource_id=request.resource_id
            )
            owners = existing_relations.get("owner", [])
            if f"user:{current_user.get('sub')}" not in owners:
                raise HTTPException(
                    status_code=403,
                    detail="Only resource owners and admins can grant relationships"
                )
        
        relationship_id = await relationship_manager.add_relationship(
            user_id=request.user_id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            relation_type=request.relation_type,
            granted_by=f"user:{current_user.get('sub')}"
        )
        
        logger.info(
            f"Relationship added: {request.user_id} -> {request.relation_type} on {request.resource_type}:{request.resource_id}"
        )
        
        return {
            "message": "Relationship added successfully",
            "relationship_id": relationship_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add relationship: {e}")
        raise HTTPException(status_code=500, detail="Failed to add relationship")

@router.delete(
    "/relationships",
    summary="Remove resource relationship",
    description="Revoke a user's relationship to a resource"
)
async def remove_relationship(
    user_id: str,
    resource_type: str,
    resource_id: str,
    relation_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Remove a relationship"""
    try:
        # Authorization check (admin or owner only)
        if current_user.get("role") != "admin":
            existing_relations = await relationship_manager.get_resource_relationships(
                resource_type=resource_type,
                resource_id=resource_id
            )
            owners = existing_relations.get("owner", [])
            if f"user:{current_user.get('sub')}" not in owners:
                raise HTTPException(status_code=403, detail="Unauthorized")
        
        await relationship_manager.remove_relationship(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            relation_type=relation_type
        )
        
        logger.info(
            f"Relationship removed: {user_id} from {resource_type}:{resource_id}"
        )
        
        return {"message": "Relationship removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove relationship: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove relationship")

@router.get(
    "/relationships/{resource_type}/{resource_id}",
    summary="Get resource relationships",
    description="List all users and their relationships to a resource"
)
async def get_resource_relationships(
    resource_type: str,
    resource_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all relationships for a resource"""
    try:
        relationships = await relationship_manager.get_resource_relationships(
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relationships": relationships
        }
    except Exception as e:
        logger.error(f"Failed to get relationships: {e}")
        raise HTTPException(status_code=500, detail="Failed to get relationships")

# ==========================================
# Capability Tokens Endpoints
# ==========================================

class CreateCapabilityTokenRequest(BaseModel):
    """Request to create a capability token"""
    resource_type: str
    resource_id: str
    action: str
    expires_in_hours: int = 24
    subject_id: Optional[str] = None  # Restrict to specific user
    max_uses: Optional[int] = None  # Limit number of uses
    description: Optional[str] = None

@router.post(
    "/tokens/create",
    summary="Create capability token",
    description="Generate a temporary token for secure resource sharing"
)
async def create_capability_token(
    request: CreateCapabilityTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a capability token for sharing resources
    
    Returns a one-time-viewable token that grants temporary access
    """
    try:
        from app.core.capability_tokens import capability_manager
        
        # Verify user has permission to create tokens for this resource
        # (must be owner or admin)
        if current_user.get("role") != "admin":
            relations = await relationship_manager.get_resource_relationships(
                resource_type=request.resource_type,
                resource_id=request.resource_id
            )
            owners = relations.get("owner", [])
            if f"user:{current_user.get('sub')}" not in owners:
                raise HTTPException(
                    status_code=403,
                    detail="Only resource owners can create capability tokens"
                )
        
        # Create token
        raw_token = await capability_manager.create_token(
            issuer_id=f"user:{current_user.get('sub')}",
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            action=request.action,
            expires_in_hours=request.expires_in_hours,
            subject_id=request.subject_id,
            max_uses=request.max_uses,
            metadata={"description": request.description}
        )
        
        logger.info(
            f"Capability token created: {current_user.get('sub')} for {request.resource_type}:{request.resource_id}"
        )
        
        return {
            "token": raw_token,
            "resource_type": request.resource_type,
            "resource_id": request.resource_id,
            "action": request.action,
            "expires_in_hours": request.expires_in_hours,
            "warning": "⚠️ Save this token now! It won't be shown again."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create capability token: {e}")
        raise HTTPException(status_code=500, detail="Failed to create token")

@router.post(
    "/tokens/verify",
    summary="Verify capability token",
    description="Check if a capability token is valid for a specific action"
)
async def verify_capability_token(
    token: str,
    resource_type: str,
    resource_id: str,
    action: str,
    subject_id: Optional[str] = None
):
    """Verify if a capability token grants access"""
    try:
        from app.core.capability_tokens import capability_manager
        
        is_valid = await capability_manager.verify_token(
            raw_token=token,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            subject_id=subject_id
        )
        
        return {
            "valid": is_valid,
            "message": "Token is valid" if is_valid else "Token invalid or expired"
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=500, detail="Token verification failed")

@router.delete(
    "/tokens/revoke",
    summary="Revoke capability token",
    description="Invalidate a capability token before expiration"
)
async def revoke_capability_token(
    token: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke a capability token"""
    try:
        from app.core.capability_tokens import capability_manager
        
        revoked = await capability_manager.revoke_token(token)
        
        if not revoked:
            raise HTTPException(status_code=404, detail="Token not found")
        
        logger.info(f"Token revoked by user {current_user.get('sub')}")
        
        return {"message": "Token revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token revocation failed: {e}")
        raise HTTPException(status_code=500, detail="Token revocation failed")


@router.delete(
    "/tokens/{token_id}",
    summary="Revoke capability token by id",
    description="Invalidate a capability token using its id"
)
async def revoke_capability_token_by_id(
    token_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke a capability token by id"""
    try:
        from app.core.capability_tokens import capability_manager

        revoked = await capability_manager.revoke_token_by_id(
            token_id=token_id,
            issuer_id=f"user:{current_user.get('sub')}"
        )

        if not revoked:
            raise HTTPException(status_code=404, detail="Token not found")

        logger.info(f"Token revoked by user {current_user.get('sub')} (id={token_id})")

        return {"message": "Token revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token revocation by id failed: {e}")
        raise HTTPException(status_code=500, detail="Token revocation failed")

@router.get(
    "/tokens/list",
    summary="List capability tokens",
    description="List all capability tokens created by current user"
)
async def list_capability_tokens(
    current_user: dict = Depends(get_current_user)
):
    """List all tokens created by the current user"""
    try:
        from app.core.capability_tokens import capability_manager
        
        tokens = await capability_manager.list_tokens(
            issuer_id=f"user:{current_user.get('sub')}"
        )

        for token in tokens:
            if token.get("_id"):
                token["_id"] = str(token["_id"])
        
        return {
            "total": len(tokens),
            "tokens": tokens
        }
    except Exception as e:
        logger.error(f"Failed to list tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tokens")


@router.get(
    "/tokens/inspect/{token}",
    summary="Inspect capability token",
    description="Return token metadata if valid"
)
async def inspect_capability_token(token: str):
    """Inspect a capability token without revealing secret"""
    try:
        from app.core.capability_tokens import capability_manager

        token_doc = await capability_manager.inspect_token(token)
        if not token_doc:
            raise HTTPException(status_code=404, detail="Token invalid or expired")

        # Check expiration
        if token_doc.get("expires_at") and datetime.utcnow() > token_doc["expires_at"]:
            raise HTTPException(status_code=400, detail="Token expirat")

        # Check max uses
        if token_doc.get("max_uses") and token_doc.get("used_count", 0) >= token_doc.get("max_uses"):
            raise HTTPException(status_code=400, detail="Token a atins limita de utilizări")

        return {
            "id": token_doc.get("_id"),
            "resource_type": token_doc.get("resource_type"),
            "resource_id": token_doc.get("resource_id"),
            "action": token_doc.get("action"),
            "expires_at": token_doc.get("expires_at"),
            "max_uses": token_doc.get("max_uses"),
            "used_count": token_doc.get("used_count", 0),
            "subject_id": token_doc.get("subject_id"),
            "metadata": token_doc.get("metadata", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token inspection failed: {e}")
        raise HTTPException(status_code=500, detail="Token inspection failed")


@router.get(
    "/tokens/resource/{token}",
    summary="Access resource via capability token",
    description="Return resource details if token is valid"
)
async def get_resource_by_token(token: str):
    """Return resource details using a capability token"""
    try:
        from app.core.capability_tokens import capability_manager

        token_doc = await capability_manager.inspect_token(token)
        if not token_doc:
            raise HTTPException(status_code=404, detail="Token invalid or expired")

        # Validate token
        is_valid = await capability_manager.verify_token(
            raw_token=token,
            resource_type=token_doc.get("resource_type"),
            resource_id=token_doc.get("resource_id"),
            action=token_doc.get("action"),
            subject_id=token_doc.get("subject_id")
        )

        if not is_valid:
            raise HTTPException(status_code=403, detail="Token invalid or expired")

        if token_doc.get("resource_type") != "parcel":
            raise HTTPException(status_code=400, detail="Unsupported resource type")

        parcel_oid = validate_object_id(token_doc.get("resource_id"), "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid})
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")

        return {
            "id": str(parcel["_id"]),
            "name": parcel.get("name"),
            "crop_type": parcel.get("crop_type"),
            "surface_ha": parcel.get("area_ha"),
            "coordinates": parcel.get("coordinates"),
            "establishment_id": parcel.get("establishment_id"),
            "created_at": parcel.get("created_at").isoformat() if parcel.get("created_at") else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token resource access failed: {e}")
        raise HTTPException(status_code=500, detail="Token resource access failed")
