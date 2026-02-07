from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.core.security import get_current_user
from app.core.database import db
from app.core.s3_storage import s3_storage
from app.core import config
from bson import ObjectId
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/establishments/{est_id}/logo")
async def upload_logo(est_id: str, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    # Validate ownership
    user_id = user.get("sub")
    est = await db["establishments"].find_one({"_id": ObjectId(est_id)})
    if not est:
        raise HTTPException(status_code=404, detail="Establishment not found")
    if str(est.get("user_id")) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this establishment")

    content = await file.read()
    filename = file.filename
    content_type = file.content_type or "application/octet-stream"

    # If AWS credentials present, upload to S3, otherwise save locally
    if config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY:
        success, s3_key, err = await s3_storage.upload_file(
            content, filename, content_type, user_id, est_id, bucket_type="main"
        )
        if not success:
            raise HTTPException(status_code=500, detail=err)
        # Save s3 key to establishment
        await db["establishments"].update_one({"_id": ObjectId(est_id)}, {"$set": {"logo_s3_key": s3_key}})
        logo_url = f"s3://{s3_storage.bucket_v3}/{s3_key}"
    else:
        upload_dir = config.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, f"est_{est_id}_{filename}")
        with open(save_path, "wb") as f:
            f.write(content)
        await db["establishments"].update_one({"_id": ObjectId(est_id)}, {"$set": {"logo_path": save_path}})
        logo_url = f"file://{save_path}"

    logger.info(f"Logo uploaded for establishment {est_id} by user {user_id}")
    return {"message": "Logo uploaded", "logo_url": logo_url}