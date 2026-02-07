"""
Multitenancy support for VitiScan v3
Provides tenant isolation and context management
"""
from typing import Optional
from contextvars import ContextVar
from fastapi import Request, HTTPException, status
from app.core.security import decode_access_token

# Context variable to store current tenant_id across async operations
current_tenant: ContextVar[Optional[str]] = ContextVar('current_tenant', default=None)

class TenantContext:
    """Manages tenant context for database queries"""
    
    @staticmethod
    def get_current_tenant() -> Optional[str]:
        """Get current tenant_id from context"""
        return current_tenant.get()
    
    @staticmethod
    def set_current_tenant(tenant_id: str):
        """Set current tenant_id in context"""
        current_tenant.set(tenant_id)
    
    @staticmethod
    def clear_tenant():
        """Clear tenant context"""
        current_tenant.set(None)
    
    @staticmethod
    def get_tenant_filter(user_id: str = None) -> dict:
        """
        Get MongoDB filter for tenant isolation
        Returns filter that ensures queries are scoped to current tenant
        """
        tenant_id = current_tenant.get()
        filter_dict = {}
        
        if tenant_id:
            filter_dict['tenant_id'] = tenant_id
        
        if user_id:
            filter_dict['user_id'] = user_id
        
        return filter_dict


async def tenant_middleware(request: Request, call_next):
    """
    Middleware to extract and set tenant context from JWT
    Runs before each request to establish tenant isolation
    """
    try:
        # Extract explicit tenant from header (preferred override)
        header_tenant = request.headers.get('X-Tenant-Id')

        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Decode JWT and extract tenant_id
                payload = decode_access_token(token)
                tenant_id = payload.get('tenant_id')
                user_id = payload.get('sub')
                
                if tenant_id:
                    TenantContext.set_current_tenant(tenant_id)
                    request.state.tenant_id = tenant_id
                    request.state.user_id = user_id
                    
            except Exception:
                # Token invalid or expired - let auth middleware handle it
                pass
        
        if header_tenant:
            TenantContext.set_current_tenant(header_tenant)
            request.state.tenant_id = header_tenant

        # Process request
        response = await call_next(request)
        
        # Clear tenant context after request
        TenantContext.clear_tenant()
        
        return response
        
    except Exception as e:
        TenantContext.clear_tenant()
        raise e


def require_tenant(request: Request) -> str:
    """
    Dependency to require tenant context
    Raises 403 if no tenant is set
    """
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context required. Please select an establishment."
        )
    
    return tenant_id


def get_user_tenants(user_id: str, db) -> list:
    """
    Get all tenants (establishments) a user belongs to
    Returns list of {tenant_id, role, establishment_name}
    """
    # Query establishment_members collection
    memberships = list(db.establishment_members.find({
        'user_id': user_id,
        'is_active': True
    }))
    
    result = []
    for member in memberships:
        # Get establishment details
        establishment = db.establishments.find_one({'id': member['establishment_id']})
        if establishment:
            result.append({
                'tenant_id': f"est:{member['establishment_id']}",
                'establishment_id': member['establishment_id'],
                'establishment_name': establishment.get('name', 'Unknown'),
                'role': member.get('role', 'member'),
                'joined_at': member.get('created_at')
            })
    
    return result


async def switch_tenant(request: Request, tenant_id: str, db) -> bool:
    """
    Switch user's active tenant
    Validates user has access to tenant
    """
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Validate user has access to this tenant
    user_tenants = get_user_tenants(user_id, db)
    tenant_ids = [t['tenant_id'] for t in user_tenants]
    
    if tenant_id not in tenant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    # Set new tenant context
    TenantContext.set_current_tenant(tenant_id)
    request.state.tenant_id = tenant_id
    
    return True
