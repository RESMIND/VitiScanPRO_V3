from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.database import db
from app.routes.auth import get_current_user
from app.core.utils import validate_object_id, sanitize_error_message
from bson import ObjectId
from typing import List
import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic model for creating an establishment
class EstablishmentCreate(BaseModel):
    name: str
    siret: str
    address: str
    surface_ha: float

# Route POST /establishments - create a new establishment
@router.post("/establishments", summary="Create a new establishment")
async def create_establishment(data: EstablishmentCreate, user: dict = Depends(get_current_user)):
    try:
        # Extract user_id from token
        user_id = user.get("sub")
        
        # Create the establishment
        establishment = {
            "name": data.name,
            "siret": data.siret,
            "address": data.address,
            "surface_ha": data.surface_ha,
            "user_id": user_id,
            "created_at": datetime.datetime.utcnow()
        }
        
        # Save to MongoDB
        result = await db["establishments"].insert_one(establishment)
        
        return {
            "id": str(result.inserted_id),
            "name": data.name,
            "siret": data.siret,
            "address": data.address,
            "surface_ha": data.surface_ha,
            "user_id": user_id,
            "created_at": establishment["created_at"].isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating establishment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating establishment")

# Route GET /establishments/mine - return all establishments of current user
@router.get("/establishments/mine", summary="Get my establishments")
async def get_my_establishments(user: dict = Depends(get_current_user)):
    try:
        # Extract user_id from token
        user_id = user.get("sub")
        
        # Find all establishments where user_id matches
        cursor = db["establishments"].find({"user_id": user_id})
        establishments = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for each establishment
        result = []
        for est in establishments:
            result.append({
                "id": str(est["_id"]),
                "name": est.get("name"),
                "siret": est.get("siret"),
                "address": est.get("address"),
                "surface_ha": est.get("surface_ha"),
                "user_id": est.get("user_id"),
                "created_at": est.get("created_at").isoformat() if est.get("created_at") else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving establishments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving establishments")
