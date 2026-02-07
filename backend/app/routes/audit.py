"""
Audit Trail endpoints for monitoring and debugging authorization
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.routes.auth import get_current_user
from app.core.database import db
from app.core.logger import logger

router = APIRouter(prefix="/admin/audit", tags=["Audit Trail"])

class AuditLogEntry(BaseModel):
    """Single audit log entry"""
    timestamp: datetime
    user_id: str
    action: str  # "authz_check", "relationship_added", "token_created", etc.
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    outcome: str  # "allow", "deny", "success", "failure"
    details: dict = {}

@router.get(
    "/logs",
    summary="Get audit trail logs",
    description="Admin-only endpoint to view authorization audit logs"
)
async def get_audit_logs(
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter until this date"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    outcome: Optional[str] = Query(None, description="Filter by outcome (allow/deny)"),
    limit: int = Query(100, le=1000, description="Max results to return"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get audit trail logs with filtering
    
    Only admins can access this endpoint
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    # Build query
    query = {}
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date
    
    if user_id:
        query["user_id"] = user_id
    
    if action:
        query["action"] = action
    
    if outcome:
        query["outcome"] = outcome
    
    # Fetch logs from audit_logs collection
    cursor = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return {
        "total": len(logs),
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "user_id": user_id,
            "action": action,
            "outcome": outcome
        },
        "logs": logs
    }

@router.get(
    "/stats",
    summary="Get audit statistics",
    description="Admin-only endpoint for authorization statistics"
)
async def get_audit_stats(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get authorization statistics
    
    Returns:
    - Total authorization checks
    - Allow vs Deny ratio
    - Most active users
    - Most accessed resources
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total checks
    total = await db.audit_logs.count_documents({
        "action": "authz_check",
        "timestamp": {"$gte": start_date}
    })
    
    # Allow count
    allowed = await db.audit_logs.count_documents({
        "action": "authz_check",
        "outcome": "allow",
        "timestamp": {"$gte": start_date}
    })
    
    # Deny count
    denied = await db.audit_logs.count_documents({
        "action": "authz_check",
        "outcome": "deny",
        "timestamp": {"$gte": start_date}
    })
    
    # Most active users (aggregation)
    pipeline = [
        {"$match": {
            "action": "authz_check",
            "timestamp": {"$gte": start_date}
        }},
        {"$group": {
            "_id": "$user_id",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    active_users = await db.audit_logs.aggregate(pipeline).to_list(length=10)
    
    # Most accessed resources
    pipeline_resources = [
        {"$match": {
            "action": "authz_check",
            "timestamp": {"$gte": start_date},
            "resource_id": {"$ne": None}
        }},
        {"$group": {
            "_id": {"type": "$resource_type", "id": "$resource_id"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    accessed_resources = await db.audit_logs.aggregate(pipeline_resources).to_list(length=10)
    
    return {
        "period_days": days,
        "total_checks": total,
        "allowed": allowed,
        "denied": denied,
        "allow_rate": round((allowed / total * 100) if total > 0 else 0, 2),
        "most_active_users": [
            {"user_id": u["_id"], "checks": u["count"]}
            for u in active_users
        ],
        "most_accessed_resources": [
            {"resource": f"{r['_id']['type']}:{r['_id']['id']}", "accesses": r["count"]}
            for r in accessed_resources
        ]
    }

@router.get(
    "/user/{user_id}",
    summary="Get user authorization history",
    description="View authorization history for a specific user"
)
async def get_user_audit_trail(
    user_id: str,
    days: int = Query(30, description="Number of days to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get authorization history for a specific user"""
    # Users can see their own history, admins can see anyone's
    if current_user.get("role") != "admin" and str(current_user["_id"]) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Can only view your own audit trail"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    cursor = db.audit_logs.find({
        "user_id": f"user:{user_id}",
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", -1).limit(100)
    
    logs = await cursor.to_list(length=100)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return {
        "user_id": user_id,
        "period_days": days,
        "total_events": len(logs),
        "events": logs
    }

async def log_audit_event(
    user_id: str,
    action: str,
    outcome: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: dict = {}
):
    """
    Helper function to log audit events
    Call this from anywhere in the app
    """
    try:
        await db.audit_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
            "details": details
        })
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

__all__ = ["router", "log_audit_event"]
