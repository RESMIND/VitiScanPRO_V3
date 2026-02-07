"""
Soft deletion and trash management
Allows recovery of deleted resources within 30 days
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.tenancy import require_tenant

router = APIRouter(prefix="/trash", tags=["Trash"])


@router.get("/")
async def list_trash(
    resource_type: Optional[str] = Query(None, description="Filter by resource type: parcel, scan, establishment"),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    List all soft-deleted resources in trash
    Items stay in trash for 30 days before permanent deletion
    """
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    trash_items = []
    
    # Get deleted parcels
    if not resource_type or resource_type == 'parcel':
        parcels = list(db.parcels.find({
            'establishment_id': establishment_id,
            'is_deleted': True,
            'deleted_at': {'$exists': True}
        }))
        
        for parcel in parcels:
            trash_items.append({
                'id': parcel['id'],
                'resource_type': 'parcel',
                'name': parcel.get('name', 'Unnamed Parcel'),
                'deleted_at': parcel['deleted_at'],
                'deleted_by': parcel.get('deleted_by'),
                'can_restore': is_restorable(parcel['deleted_at']),
                'days_until_permanent': get_days_until_permanent(parcel['deleted_at']),
                'metadata': {
                    'surface_ha': parcel.get('surface_ha'),
                    'crop_type': parcel.get('crop_type')
                }
            })
    
    # Get deleted scans
    if not resource_type or resource_type == 'scan':
        scans = list(db.scans.find({
            'user_id': current_user['id'],
            'is_deleted': True,
            'deleted_at': {'$exists': True}
        }))
        
        for scan in scans:
            trash_items.append({
                'id': scan['id'],
                'resource_type': 'scan',
                'name': f"Scan {scan.get('scan_date', 'Unknown')}",
                'deleted_at': scan['deleted_at'],
                'deleted_by': scan.get('deleted_by'),
                'can_restore': is_restorable(scan['deleted_at']),
                'days_until_permanent': get_days_until_permanent(scan['deleted_at']),
                'metadata': {
                    'parcel_id': scan.get('parcel_id'),
                    'scan_date': scan.get('scan_date'),
                    'status': scan.get('status')
                }
            })
    
    # Sort by deleted_at (newest first)
    trash_items.sort(key=lambda x: x['deleted_at'], reverse=True)
    
    return {
        'items': trash_items,
        'total': len(trash_items),
        'retention_days': 30
    }


@router.post("/restore/{resource_type}/{resource_id}")
async def restore_from_trash(
    resource_type: str,
    resource_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    Restore a soft-deleted resource from trash
    Only available within 30 days of deletion
    """
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    if resource_type == 'parcel':
        collection = db.parcels
        filter_query = {
            'id': resource_id,
            'establishment_id': establishment_id,
            'is_deleted': True
        }
    elif resource_type == 'scan':
        collection = db.scans
        filter_query = {
            'id': resource_id,
            'user_id': current_user['id'],
            'is_deleted': True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resource type: {resource_type}"
        )
    
    # Find deleted resource
    resource = collection.find_one(filter_query)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found in trash"
        )
    
    # Check if still restorable
    if not is_restorable(resource['deleted_at']):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"{resource_type.capitalize()} cannot be restored (retention period expired)"
        )
    
    # Restore resource
    collection.update_one(
        filter_query,
        {
            '$set': {
                'is_deleted': False,
                'restored_at': datetime.utcnow().isoformat(),
                'restored_by': current_user['id']
            },
            '$unset': {
                'deleted_at': '',
                'deleted_by': ''
            }
        }
    )
    
    # Log audit
    db.audit_logs.insert_one({
        'user_id': current_user['id'],
        'tenant_id': tenant_id,
        'action': f'{resource_type}.restored',
        'resource_type': resource_type,
        'resource_id': resource_id,
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': {
            'resource_name': resource.get('name', 'Unknown')
        }
    })
    
    return {
        'message': f'{resource_type.capitalize()} restored successfully',
        'resource_id': resource_id,
        'resource_type': resource_type
    }


@router.delete("/permanent/{resource_type}/{resource_id}")
async def permanent_delete(
    resource_type: str,
    resource_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    Permanently delete a resource from trash
    This action cannot be undone
    """
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    if resource_type == 'parcel':
        collection = db.parcels
        filter_query = {
            'id': resource_id,
            'establishment_id': establishment_id,
            'is_deleted': True
        }
    elif resource_type == 'scan':
        collection = db.scans
        filter_query = {
            'id': resource_id,
            'user_id': current_user['id'],
            'is_deleted': True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resource type: {resource_type}"
        )
    
    # Find deleted resource
    resource = collection.find_one(filter_query)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found in trash"
        )
    
    # Permanently delete
    collection.delete_one(filter_query)
    
    # Log audit
    db.audit_logs.insert_one({
        'user_id': current_user['id'],
        'tenant_id': tenant_id,
        'action': f'{resource_type}.permanent_delete',
        'resource_type': resource_type,
        'resource_id': resource_id,
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': {
            'resource_name': resource.get('name', 'Unknown'),
            'warning': 'PERMANENT_DELETION'
        }
    })
    
    return {
        'message': f'{resource_type.capitalize()} permanently deleted',
        'resource_id': resource_id
    }


@router.delete("/empty")
async def empty_trash(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant),
    db = Depends(get_db)
):
    """
    Empty entire trash - permanently delete all items
    This action cannot be undone
    """
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    # Delete all trashed parcels
    parcels_result = db.parcels.delete_many({
        'establishment_id': establishment_id,
        'is_deleted': True
    })
    
    # Delete all trashed scans
    scans_result = db.scans.delete_many({
        'user_id': current_user['id'],
        'is_deleted': True
    })
    
    total_deleted = parcels_result.deleted_count + scans_result.deleted_count
    
    # Log audit
    db.audit_logs.insert_one({
        'user_id': current_user['id'],
        'tenant_id': tenant_id,
        'action': 'trash.emptied',
        'resource_type': 'trash',
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': {
            'parcels_deleted': parcels_result.deleted_count,
            'scans_deleted': scans_result.deleted_count,
            'total_deleted': total_deleted,
            'warning': 'PERMANENT_DELETION'
        }
    })
    
    return {
        'message': 'Trash emptied successfully',
        'items_deleted': total_deleted,
        'parcels': parcels_result.deleted_count,
        'scans': scans_result.deleted_count
    }


def is_restorable(deleted_at: str) -> bool:
    """Check if resource can still be restored (within 30 days)"""
    deleted_time = datetime.fromisoformat(deleted_at)
    expiry_time = deleted_time + timedelta(days=30)
    return datetime.utcnow() < expiry_time


def get_days_until_permanent(deleted_at: str) -> int:
    """Get number of days until permanent deletion"""
    deleted_time = datetime.fromisoformat(deleted_at)
    expiry_time = deleted_time + timedelta(days=30)
    days_left = (expiry_time - datetime.utcnow()).days
    return max(0, days_left)
