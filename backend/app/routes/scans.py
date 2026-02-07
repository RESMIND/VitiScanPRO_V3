from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from app.core.database import db
from app.routes.auth import get_current_user
from app.core.rbac import require_capability
from app.core.utils import validate_object_id, sanitize_error_message
from app.routes.audit import log_audit_event
from app.core.s3_storage import s3_storage
from app.core.config import MAX_FILE_SIZE_BYTES, ALLOWED_FILE_EXTENSIONS, ALLOWED_MIME_TYPES
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Scans"])

class ScanInfo(BaseModel):
    scan_id: str
    filename: str
    uploaded_at: datetime

class ScanUploadResponse(BaseModel):
    message: str
    scan_id: str
    s3_key: str

class ScanOut(BaseModel):
    id: str
    filename: str
    content_type: str | None = None
    file_size: int | None = None
    parcel_id: str
    user_id: str
    uploaded_at: datetime | None = None
    s3_key: str | None = None
    s3_bucket: str | None = None

@router.post(
    "/scans/{parcel_id}/upload",
    summary="Încarcă o scanare pentru o parcelă",
    response_model=ScanUploadResponse,
    responses={
        201: {"description": "Upload reușit"},
        400: {"description": "Fișier invalid"},
        413: {"description": "Fișier prea mare"}
    },
    status_code=201
)
async def upload_scan(
    parcel_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(require_capability("scan:upload"))
):
    try:
        # Validate parcel ownership
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user.get("sub")})
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        # V5.1 FIX: Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Type de fichier {file_ext} non autorisé. Types autorisés : {', '.join(ALLOWED_FILE_EXTENSIONS)}"
            )
        
        # V5.1 FIX: Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Type MIME {file.content_type} non autorisé. Types autorisés : {', '.join(ALLOWED_MIME_TYPES)}"
            )

        # Read file content
        content = await file.read()
        
        # V5.1 FIX: Validate file size
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Fichier trop volumineux. Taille maximale : {MAX_FILE_SIZE_BYTES / (1024 * 1024):.1f}MB"
            )
        
        # V5.1 FIX: Validate magic bytes (file signature)
        if file_ext in [".jpg", ".jpeg"]:
            if not content[:3] == b'\xff\xd8\xff':
                raise HTTPException(status_code=400, detail="Signature de fichier JPEG invalide")
        elif file_ext == ".png":
            if not content[:4] == b'\x89PNG':
                raise HTTPException(status_code=400, detail="Signature de fichier PNG invalide")
        elif file_ext in [".tiff", ".tif"]:
            if not (content[:2] == b'II' or content[:2] == b'MM'):
                raise HTTPException(status_code=400, detail="Signature de fichier TIFF invalide")
        elif file_ext == ".pdf":
            if not content[:4] == b'%PDF':
                raise HTTPException(status_code=400, detail="Signature de fichier PDF invalide")
        
        # Upload to S3
        success, s3_key, error = await s3_storage.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=user.get("sub"),
            parcel_id=parcel_id,
            bucket_type="main"
        )
        
        if not success:
            logger.error(f"S3 upload failed: {error}")
            raise HTTPException(status_code=500, detail="Error uploading file to storage")

        # Save metadata to MongoDB (without file_data)
        scan = {
            "filename": file.filename,
            "content_type": file.content_type or "application/octet-stream",
            "s3_key": s3_key,  # Store S3 key instead of file data
            "s3_bucket": "main",
            "file_size": len(content),
            "user_id": user.get("sub"),
            "parcel_id": parcel_id,
            "uploaded_at": datetime.utcnow()
        }

        result = await db["scans"].insert_one(scan)
        logger.info(f"Scan metadata saved for user {user.get('sub')}, file: {file.filename}")

        await log_audit_event(
            user_id=user.get("sub"),
            action="scan.upload",
            outcome="success",
            resource_type="scan",
            resource_id=str(result.inserted_id),
            details={"parcel_id": parcel_id, "filename": file.filename}
        )
        
        return {"message": "Scan uploaded", "scan_id": str(result.inserted_id), "s3_key": s3_key}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading scan: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.get(
    "/scans/by-parcel/{parcel_id}",
    summary="Listează scanările unei parcele",
    response_model=List[ScanInfo]
)
async def get_scans_by_parcel(
    parcel_id: str,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(require_capability("scan:view"))
):
    try:
        # Validate that the parcel belongs to the user
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user.get("sub")})
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        # Find scans for this parcel with pagination
        scans_cursor = db["scans"].find({"parcel_id": parcel_id, "user_id": user.get("sub")})\
            .skip(offset).limit(limit)
        scans = []
        async for scan in scans_cursor:
            scans.append({
                "scan_id": str(scan["_id"]),
                "filename": scan["filename"],
                "uploaded_at": scan["uploaded_at"]
            })

        return scans

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scans: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.get(
    "/scans/{scan_id}",
    summary="Descarcă o scanare",
    response_model=ScanOut,
    responses={
        200: {"description": "Fișier descărcat"},
        404: {"description": "Scanare inexistentă"}
    }
)
async def download_scan(
    scan_id: str,
    user: dict = Depends(require_capability("scan:view"))
):
    try:
        scan_oid = validate_object_id(scan_id, "scan_id")
        scan = await db["scans"].find_one({"_id": scan_oid, "user_id": user.get("sub")})
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found or access denied")

        # Download from S3
        s3_key = scan.get("s3_key")
        s3_bucket_type = scan.get("s3_bucket", "main")
        
        if not s3_key:
            # Fallback for old scans still in MongoDB
            if "file_data" in scan:
                logger.warning(f"Scan {scan_id} using legacy MongoDB storage")
                return Response(
                    content=scan["file_data"],
                    media_type=scan["content_type"],
                    headers={"Content-Disposition": f'attachment; filename="{scan["filename"]}"'}
                )
            else:
                raise HTTPException(status_code=500, detail="Scan file location not found")
        
        success, file_content, content_type, error = await s3_storage.download_file(
            s3_key=s3_key,
            bucket_type=s3_bucket_type
        )
        
        if not success:
            logger.error(f"S3 download failed: {error}")
            raise HTTPException(status_code=500, detail="Error downloading file from storage")

        return Response(
            content=file_content,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{scan["filename"]}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading scan: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))
