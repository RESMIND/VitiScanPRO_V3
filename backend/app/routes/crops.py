from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from app.core.database import db
from app.routes.auth import get_current_user
from app.core.rbac import require_capability
from app.core.utils import validate_object_id, sanitize_error_message
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Crops"])

class CropCreate(BaseModel):
    name: str
    variety: str | None = None
    year: int
    parcel_id: str

class CropOut(BaseModel):
    id: str
    name: str
    variety: str | None = None
    year: int
    parcel_id: str
    user_id: str
    created_at: str | None = None

class CropActionResponse(BaseModel):
    message: str
    crop_id: str | None = None

@router.post(
    "/crops",
    summary="Creează o cultură",
    response_model=CropActionResponse,
    responses={
        201: {"description": "Cultură creată"},
        400: {"description": "Eroare de validare"}
    },
    status_code=201
)
async def create_crop(
    data: CropCreate,
    user: dict = Depends(require_capability("crop:update"))
):
    try:
        parcel_oid = validate_object_id(data.parcel_id, "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user.get("sub")})
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        crop = {
            "name": data.name,
            "variety": data.variety,
            "year": data.year,
            "parcel_id": data.parcel_id,
            "user_id": user.get("sub"),
            "created_at": datetime.utcnow()
        }

        result = await db["crops"].insert_one(crop)
        return {"message": "Crop created", "crop_id": str(result.inserted_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating crop: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.get(
    "/crops/by-parcel/{parcel_id}",
    summary="Listează culturile unei parcele",
    response_model=list[CropOut]
)
async def get_crops_by_parcel(
    parcel_id: str,
    user: dict = Depends(require_capability("parcel:view"))
):
    try:
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user.get("sub")})
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        crops_cursor = db["crops"].find({"parcel_id": parcel_id, "user_id": user.get("sub")})
        crops = []
        async for crop in crops_cursor:
            crops.append({
                "id": str(crop["_id"]),
                "name": crop.get("name"),
                "variety": crop.get("variety"),
                "year": crop.get("year"),
                "parcel_id": crop.get("parcel_id"),
                "user_id": crop.get("user_id"),
                "created_at": crop.get("created_at").isoformat() if crop.get("created_at") else None
            })
        return crops

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving crops: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.put(
    "/crops/{crop_id}",
    summary="Actualizează o cultură",
    response_model=CropActionResponse
)
async def update_crop(
    crop_id: str,
    crop_data: CropCreate,
    user: dict = Depends(require_capability("crop:update"))
):
    try:
        crop_oid = validate_object_id(crop_id, "crop_id")
        crop = await db["crops"].find_one({"_id": crop_oid, "user_id": user.get("sub")})
        if not crop:
            raise HTTPException(status_code=404, detail="Crop not found or access denied")

        await db["crops"].update_one(
            {"_id": crop_oid},
            {"$set": crop_data.dict()}
        )
        return {"message": "Crop updated successfully", "crop_id": crop_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating crop: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.delete(
    "/crops/{crop_id}",
    summary="Șterge o cultură",
    response_model=CropActionResponse
)
async def delete_crop(
    crop_id: str,
    user: dict = Depends(require_capability("crop:update"))
):
    try:
        crop_oid = validate_object_id(crop_id, "crop_id")
        crop = await db["crops"].find_one({"_id": crop_oid, "user_id": user.get("sub")})
        if not crop:
            raise HTTPException(status_code=404, detail="Crop not found or access denied")

        await db["crops"].delete_one({"_id": crop_oid})
        return {"message": "Crop deleted successfully", "crop_id": crop_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting crop: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))
