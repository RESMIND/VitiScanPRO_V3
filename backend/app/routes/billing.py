from fastapi import APIRouter, Depends, HTTPException
from app.routes.auth import get_current_user
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])

FREE_LIMITS = {
    "parcels": 3,
    "scans_per_month": 10,
    "storage_mb": 100,
    "team_members": 1
}


@router.get("/usage", summary="Get usage stats")
async def get_usage_stats(user: dict = Depends(get_current_user)):
    """Return usage stats for current user (placeholder plan logic)."""
    try:
        user_id = user.get("sub")
        parcels_count = await db["parcels"].count_documents({"user_id": user_id})
        scans_count = await db["scans"].count_documents({"user_id": user_id})

        # Storage used (MB)
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
        ]
        agg = await db["scans"].aggregate(pipeline).to_list(length=1)
        total_size_bytes = agg[0]["total_size"] if agg else 0
        storage_mb = total_size_bytes / (1024 ** 2)

        return {
            "plan": "free",
            "usage": {
                "parcels": {
                    "current": parcels_count,
                    "limit": FREE_LIMITS["parcels"],
                    "unlimited": False
                },
                "scans_this_month": {
                    "current": scans_count,
                    "limit": FREE_LIMITS["scans_per_month"],
                    "unlimited": False
                },
                "team_members": {
                    "current": 1,
                    "limit": FREE_LIMITS["team_members"],
                    "unlimited": False
                },
                "storage_mb": {
                    "current": round(storage_mb, 2),
                    "limit": FREE_LIMITS["storage_mb"],
                    "unlimited": False
                }
            }
        }
    except Exception as e:
        logger.error(f"Error loading usage stats: {e}")
        raise HTTPException(status_code=500, detail="Error loading usage stats")


@router.post("/create-checkout", summary="Create checkout session")
async def create_checkout_session(payload: dict, user: dict = Depends(get_current_user)):
    """Placeholder endpoint for billing checkout."""
    try:
        plan_id = payload.get("plan_id")
        if not plan_id:
            raise HTTPException(status_code=400, detail="plan_id is required")

        return {
            "checkout_url": "/billing/unavailable",
            "message": "Checkout is not configured in this environment"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Error creating checkout session")
