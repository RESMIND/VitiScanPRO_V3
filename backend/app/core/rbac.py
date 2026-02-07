from fastapi import Depends, HTTPException
from app.core.database import db
from app.core.tenancy import require_tenant
from app.routes.auth import get_current_user

# Capability map per role (establishment-scoped)
ROLE_CAPABILITIES = {
    "admin": {"*"},
    "operator": {
        "parcel:view",
        "parcel:create",
        "parcel:update",
        "treatment:view",
        "treatment:create",
        "scan:view",
        "scan:upload",
        "crop:update",
        "pdf:export",
        "team:view",
    },
    "viewer": {
        "parcel:view",
        "treatment:view",
        "scan:view",
        "pdf:export",
        "team:view",
    },
    "invitee": set(),
}


def _normalize_member_role(member_role: str | None) -> str:
    if not member_role:
        return "invitee"
    role = member_role.lower()
    if role in {"owner", "admin"}:
        return "admin"
    if role in {"member", "consultant", "operator"}:
        return "operator"
    if role == "viewer":
        return "viewer"
    return "invitee"


def _has_capability(role: str, capability: str) -> bool:
    caps = ROLE_CAPABILITIES.get(role, set())
    return "*" in caps or capability in caps


def require_capability(capability: str):
    async def _guard(
        user: dict = Depends(get_current_user),
        tenant_id: str = Depends(require_tenant)
    ):
        # System admin bypass
        if user.get("role") == "admin":
            return user

        establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
        member = await db.establishment_members.find_one({
            "establishment_id": establishment_id,
            "user_id": user.get("sub"),
            "is_active": True
        })

        role = _normalize_member_role(member.get("role") if member else None)
        if not _has_capability(role, capability):
            raise HTTPException(status_code=403, detail="Access denied")

        return user

    return _guard


__all__ = ["require_capability", "ROLE_CAPABILITIES"]