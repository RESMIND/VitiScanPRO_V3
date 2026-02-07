"""
Team invitations and member management
Allows establishment owners to invite users to their team
"""
from datetime import datetime, timedelta
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.notifications import email_notifier
from app.core import config
from app.core.security import get_current_user
from app.core.rbac import require_capability
from app.core.tenancy import require_tenant, get_user_tenants

router = APIRouter(prefix="/invitations", tags=["Invitations"])


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "member"  # member, consultant, viewer
    expires_in_days: int = 7


class InvitationResponse(BaseModel):
    id: str
    establishment_id: str
    establishment_name: str
    email: str
    role: str
    status: str  # pending, accepted, expired, revoked
    invite_code: str
    invited_by: str
    created_at: str
    expires_at: str


class AcceptInvitation(BaseModel):
    invite_code: str

class MemberOut(BaseModel):
    id: str
    user_id: str
    email: str | None = None
    full_name: str | None = None
    role: str
    joined_at: str | None = None
    is_owner: bool

class MessageResponse(BaseModel):
    message: str

class InvitationAcceptResponse(BaseModel):
    message: str
    establishment_id: str
    establishment_name: str
    role: str


@router.post(
    "/",
    summary="Creează invitație",
    response_model=InvitationResponse,
    responses={
        201: {"description": "Invitație creată"},
        403: {"description": "Acces interzis"}
    },
    status_code=status.HTTP_201_CREATED
)
async def create_invitation(
    data: InvitationCreate,
    current_user: dict = Depends(require_capability("team:invite")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    Create invitation to join establishment
    Only owners and admins can invite
    """
    # Extract establishment_id from tenant_id (format: "est:uuid")
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    # Check if user has permission to invite (owner or admin)
    member = db.establishment_members.find_one({
        'establishment_id': establishment_id,
        'user_id': current_user['id'],
        'is_active': True
    })
    
    if not member or member.get('role') not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les propriétaires et les administrateurs peuvent inviter des membres"
        )
    
    # Check if user is already a member
    existing_member = db.establishment_members.find_one({
        'establishment_id': establishment_id,
        'email': data.email,
        'is_active': True
    })
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur est déjà membre de cet établissement"
        )
    
    # Check for pending invitation
    pending = db.invitations.find_one({
        'establishment_id': establishment_id,
        'email': data.email,
        'status': 'pending'
    })
    
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation déjà envoyée à cet e-mail"
        )
    
    # Get establishment details
    establishment = db.establishments.find_one({'id': establishment_id})
    if not establishment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Establishment not found"
        )
    
    # Generate unique invite code
    invite_code = secrets.token_urlsafe(32)
    invitation_id = f"inv:{secrets.token_urlsafe(16)}"
    
    # Create invitation
    invitation = {
        'id': invitation_id,
        'establishment_id': establishment_id,
        'establishment_name': establishment['name'],
        'email': data.email,
        'role': data.role,
        'status': 'pending',
        'invite_code': invite_code,
        'invited_by': current_user['id'],
        'invited_by_name': current_user.get('full_name', 'Unknown'),
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(days=data.expires_in_days)).isoformat()
    }
    
    db.invitations.insert_one(invitation)
    
    # Send invitation email
    await email_notifier.send_invitation_email(
        to_email=data.email,
        inviter_name=current_user.get('full_name', 'VitiScan'),
        establishment_name=establishment.get('name', 'VitiScan'),
        invite_code=invite_code,
        base_url=config.FRONTEND_BASE_URL,
        expires_at=invitation['expires_at']
    )
    
    return InvitationResponse(**invitation)


@router.get(
    "/",
    summary="Listează invitațiile",
    response_model=list[InvitationResponse]
)
async def list_invitations(
    current_user: dict = Depends(require_capability("team:view")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """List all invitations for current establishment"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    invitations = list(db.invitations.find({
        'establishment_id': establishment_id
    }).sort('created_at', -1))
    
    return [InvitationResponse(**inv) for inv in invitations]


@router.post(
    "/accept",
    summary="Acceptă invitația",
    response_model=InvitationAcceptResponse,
    responses={200: {"description": "Invitație acceptată"}, 400: {"description": "Invitație invalidă"}}
)
async def accept_invitation(
    data: AcceptInvitation,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Accept invitation and join establishment"""
    
    # Find invitation
    invitation = db.invitations.find_one({
        'invite_code': data.invite_code,
        'status': 'pending'
    })
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already used"
        )
    
    # Check if expired
    expires_at = datetime.fromisoformat(invitation['expires_at'])
    if datetime.utcnow() > expires_at:
        db.invitations.update_one(
            {'id': invitation['id']},
            {'$set': {'status': 'expired'}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Check if invitation email matches user email
    if invitation['email'].lower() != current_user.get('email', '').lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address"
        )
    
    # Check if already a member
    existing = db.establishment_members.find_one({
        'establishment_id': invitation['establishment_id'],
        'user_id': current_user['id'],
        'is_active': True
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this establishment"
        )
    
    # Create membership
    member_id = f"mem:{secrets.token_urlsafe(16)}"
    member = {
        'id': member_id,
        'establishment_id': invitation['establishment_id'],
        'user_id': current_user['id'],
        'email': current_user['email'],
        'role': invitation['role'],
        'is_active': True,
        'created_at': datetime.utcnow().isoformat(),
        'invited_by': invitation['invited_by']
    }
    
    db.establishment_members.insert_one(member)
    
    # Mark invitation as accepted
    db.invitations.update_one(
        {'id': invitation['id']},
        {'$set': {
            'status': 'accepted',
            'accepted_at': datetime.utcnow().isoformat(),
            'accepted_by': current_user['id']
        }}
    )
    
    # Log audit
    db.audit_logs.insert_one({
        'user_id': current_user['id'],
        'tenant_id': f"est:{invitation['establishment_id']}",
        'action': 'invitation.accepted',
        'resource_type': 'invitation',
        'resource_id': invitation['id'],
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': {
            'establishment_id': invitation['establishment_id'],
            'role': invitation['role']
        }
    })
    
    return {
        'message': 'Invitation accepted successfully',
        'establishment_id': invitation['establishment_id'],
        'establishment_name': invitation['establishment_name'],
        'role': invitation['role']
    }


@router.delete(
    "/{invitation_id}",
    summary="Revocă invitația",
    response_model=MessageResponse,
    responses={200: {"description": "Invitație revocată"}, 404: {"description": "Invitație inexistentă"}}
)
async def revoke_invitation(
    invitation_id: str,
    current_user: dict = Depends(require_capability("team:invite")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """Revoke pending invitation"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    # Check permission
    member = db.establishment_members.find_one({
        'establishment_id': establishment_id,
        'user_id': current_user['id'],
        'is_active': True
    })
    
    if not member or member.get('role') not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can revoke invitations"
        )
    
    # Revoke invitation
    result = db.invitations.update_one(
        {
            'id': invitation_id,
            'establishment_id': establishment_id,
            'status': 'pending'
        },
        {'$set': {
            'status': 'revoked',
            'revoked_at': datetime.utcnow().isoformat(),
            'revoked_by': current_user['id']
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    return {'message': 'Invitation revoked successfully'}


@router.get(
    "/members",
    summary="Listează membrii echipei",
    response_model=list[MemberOut]
)
async def list_members(
    current_user: dict = Depends(require_capability("team:view")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """List all members of current establishment"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    members = list(db.establishment_members.find({
        'establishment_id': establishment_id,
        'is_active': True
    }))
    
    # Enrich with user details
    result = []
    for member in members:
        user = db.users.find_one({'id': member['user_id']})
        if user:
            result.append({
                'id': member['id'],
                'user_id': member['user_id'],
                'email': user.get('email'),
                'full_name': user.get('full_name'),
                'role': member.get('role', 'member'),
                'joined_at': member.get('created_at'),
                'is_owner': member.get('role') == 'owner'
            })
    
    return result


@router.patch(
    "/members/{member_id}/role",
    summary="Schimbă rolul unui membru",
    response_model=MessageResponse
)
async def update_member_role(
    member_id: str,
    role: str,
    current_user: dict = Depends(require_capability("team:assign-role")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """Update member role (owner/admin only)"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    # Check permission
    requester = db.establishment_members.find_one({
        'establishment_id': establishment_id,
        'user_id': current_user['id'],
        'is_active': True
    })
    
    if not requester or requester.get('role') != 'owner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can change member roles"
        )
    
    # Validate role
    valid_roles = ['member', 'consultant', 'viewer', 'admin']
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Update role
    result = db.establishment_members.update_one(
        {
            'id': member_id,
            'establishment_id': establishment_id,
            'is_active': True
        },
        {'$set': {'role': role, 'updated_at': datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return {'message': 'Member role updated successfully', 'new_role': role}


@router.delete(
    "/members/{member_id}",
    summary="Elimină membru din echipă",
    response_model=MessageResponse
)
async def remove_member(
    member_id: str,
    current_user: dict = Depends(require_capability("team:assign-role")),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """Remove member from establishment (owner/admin only)"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    # Check permission
    requester = db.establishment_members.find_one({
        'establishment_id': establishment_id,
        'user_id': current_user['id'],
        'is_active': True
    })
    
    if not requester or requester.get('role') not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can remove members"
        )
    
    # Can't remove owner
    member_to_remove = db.establishment_members.find_one({'id': member_id})
    if member_to_remove and member_to_remove.get('role') == 'owner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove establishment owner"
        )
    
    # Remove member (soft delete)
    result = db.establishment_members.update_one(
        {
            'id': member_id,
            'establishment_id': establishment_id
        },
        {'$set': {
            'is_active': False,
            'removed_at': datetime.utcnow().isoformat(),
            'removed_by': current_user['id']
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return {'message': 'Member removed successfully'}
