"""
FastAPI decorators for authorization checks
Makes authorization checks clean and declarative
"""
from functools import wraps
from typing import Optional, List, Callable
from fastapi import HTTPException, Depends
from app.core.authz_engine import authz_engine, AuthzSubject, AuthzResource, ResourceType
from app.routes.auth import get_current_user
from app.models.relationships import RelationshipManager
from app.core.database import db
from app.core.logger import logger

relationship_manager = RelationshipManager(db)

def authz_required(
    action: str,
    resource_type: ResourceType,
    get_resource_id: Optional[Callable] = None,
    require_mfa: bool = False
):
    """
    Decorator for automatic authorization checks
    
    Usage:
        @router.get("/parcels/{parcel_id}")
        @authz_required(action="view", resource_type=ResourceType.PARCEL, get_resource_id=lambda args: args['parcel_id'])
        async def get_parcel(parcel_id: str, current_user: dict = Depends(get_current_user)):
            # Authorization already checked!
            return await db.parcels.find_one({"_id": ObjectId(parcel_id)})
    
    Args:
        action: Action to check (view, edit, delete, etc.)
        resource_type: Type of resource (parcel, establishment, etc.)
        get_resource_id: Function to extract resource_id from route params
        require_mfa: Force MFA requirement for this endpoint
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Get resource_id
            resource_id = None
            if get_resource_id:
                resource_id = get_resource_id(kwargs)
            
            # Build subject
            subject = AuthzSubject(
                id=f"user:{current_user['_id']}",
                role=current_user.get('role', 'user'),
                attrs={
                    "mfa": current_user.get('mfa_enabled', False),
                    "region": current_user.get('region'),
                    "risk_score": current_user.get('risk_score', 0)
                }
            )
            
            # MFA check
            if require_mfa and not subject.attrs.get('mfa'):
                logger.warning(f"MFA required but not enabled for user {subject.id}")
                raise HTTPException(
                    status_code=403,
                    detail="Multi-Factor Authentication required for this action"
                )
            
            # Get resource relationships (if resource_id provided)
            relations = {}
            resource_attrs = {}
            if resource_id:
                # Fetch resource to get attributes and relationships
                collection_name = f"{resource_type}s"  # parcels, establishments, etc.
                resource_doc = await db[collection_name].find_one({"_id": resource_id})
                
                if resource_doc:
                    resource_attrs = {
                        "region": resource_doc.get("region"),
                        "certified": resource_doc.get("certified", False)
                    }
                
                # Get relationships
                relations = await relationship_manager.get_resource_relationships(
                    resource_type=resource_type,
                    resource_id=f"{resource_type}:{resource_id}"
                )
            
            # Build resource
            resource = AuthzResource(
                id=f"{resource_type}:{resource_id}" if resource_id else f"{resource_type}:*",
                type=resource_type,
                attrs=resource_attrs,
                relations=relations
            )
            
            # Check authorization
            decision = authz_engine.check(subject, action, resource)
            
            if decision.outcome != "allow":
                logger.warning(
                    f"Authorization denied: {subject.id} {action} {resource.id} - {decision.reasons}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Unauthorized: {', '.join(decision.reasons)}"
                )
            
            logger.info(
                f"Authorization granted: {subject.id} {action} {resource.id}"
            )
            
            # Execute original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*allowed_roles: str):
    """
    Simple role-based decorator
    
    Usage:
        @router.delete("/admin/users/{user_id}")
        @require_role("admin")
        async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
            # Only admins can access
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_role = current_user.get('role', 'user')
            if user_role not in allowed_roles:
                logger.warning(
                    f"Role check failed: user {current_user['_id']} has role {user_role}, required one of {allowed_roles}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires role: {' or '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_mfa():
    """
    MFA requirement decorator
    
    Usage:
        @router.delete("/parcels/{id}")
        @require_mfa()
        async def delete_parcel(id: str, current_user: dict = Depends(get_current_user)):
            # MFA required
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if not current_user.get('mfa_enabled', False):
                logger.warning(f"MFA check failed for user {current_user['_id']}")
                raise HTTPException(
                    status_code=403,
                    detail="Multi-Factor Authentication required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


__all__ = ["authz_required", "require_role", "require_mfa"]
