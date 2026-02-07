from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional
from app.core.security import get_current_user
from app.core.logger import logger

router = APIRouter()

class OnboardingCompleteRequest(BaseModel):
    establishment_name: str
    address: Optional[str] = None
    siret: Optional[str] = None
    total_area_ha: Optional[float] = None

@router.get("/status")
async def onboarding_status(user: dict = Depends(get_current_user)):
    """Return onboarding completion status for current user"""
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    from app.core.database import db
    db_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"onboarding_completed": bool(db_user.get("onboarding_completed", False))}

@router.post("/complete", status_code=201)
async def onboarding_complete(request: Request, data: OnboardingCompleteRequest, user: dict = Depends(get_current_user)):
    """Complete onboarding by creating a default establishment and marking user as completed"""
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    from app.core.database import db
    # Ensure user's phone is verified before completing onboarding
    db_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.get("phone_verified", False):
        raise HTTPException(status_code=400, detail="Phone number must be verified before completing onboarding")

    # Create establishment
    est = {
        "name": data.establishment_name,
        "address": data.address,
        "siret": data.siret,
        "total_area_ha": data.total_area_ha,
        "user_id": ObjectId(user_id),
        "created_at": request.state and getattr(request.state, "start_time", None)
    }
    result = await db["establishments"].insert_one(est)

    # Update user onboarding flag and default establishment
    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"onboarding_completed": True, "default_establishment_id": result.inserted_id}})

    logger.info(f"Onboarding completed for user {user_id}, created establishment {result.inserted_id}")
    return {"message": "Onboarding completed", "establishment_id": str(result.inserted_id)}
