from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.core.database import db
from app.routes.auth import get_current_admin_user
from app.core.utils import sanitize_error_message
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/global", tags=["Admin Global"])


@router.get("/stats", summary="Get global admin stats")
async def get_global_stats(admin: dict = Depends(get_current_admin_user)):
    """Return global statistics for admin dashboard"""
    try:
        total_users = await db["users"].count_documents({})
        total_establishments = await db["establishments"].count_documents({})
        total_parcels = await db["parcels"].count_documents({})
        total_scans = await db["scans"].count_documents({})

        now = datetime.utcnow()
        start_today = datetime(now.year, now.month, now.day)
        start_week = start_today - timedelta(days=7)

        scans_today = await db["scans"].count_documents({"uploaded_at": {"$gte": start_today}})
        scans_this_week = await db["scans"].count_documents({"uploaded_at": {"$gte": start_week}})

        # Storage used (GB)
        pipeline = [{"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}]
        agg = await db["scans"].aggregate(pipeline).to_list(length=1)
        total_size_bytes = agg[0]["total_size"] if agg else 0
        storage_used_gb = total_size_bytes / (1024 ** 3)

        return {
            "total_users": total_users,
            "active_users": total_users,
            "total_establishments": total_establishments,
            "total_parcels": total_parcels,
            "total_scans": total_scans,
            "scans_today": scans_today,
            "scans_this_week": scans_this_week,
            "storage_used_gb": storage_used_gb,
        }
    except Exception as e:
        logger.error(f"Error computing global stats: {e}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


@router.get("/recent-users", summary="Get recent users")
async def get_recent_users(limit: int = 10, admin: dict = Depends(get_current_admin_user)):
    """Return recently created users for admin dashboard"""
    try:
        cursor = db["users"].find({}).sort("created_at", -1).limit(limit)
        users = await cursor.to_list(length=limit)

        result = []
        for user in users:
            result.append({
                "id": str(user.get("_id")),
                "email": user.get("email") or user.get("username"),
                "full_name": user.get("full_name") or user.get("username"),
                "role": user.get("role", "user"),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                "is_active": user.get("is_active", True),
                "plan": user.get("plan", "free")
            })

        return result
    except Exception as e:
        logger.error(f"Error fetching recent users: {e}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))
