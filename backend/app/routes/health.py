"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
from app.core.database import db
from app.core.logger import logger
import boto3
from botocore.exceptions import ClientError
from app.core import config

router = APIRouter(prefix="/health", tags=["Monitoring"])

# Store app start time
START_TIME = time.time()

@router.get("")
async def health_check():
    """
    Basic health check endpoint
    Returns: Service status and uptime
    """
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
        "service": "VitiScan v3 API"
    }

@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with service dependencies
    Checks: MongoDB, S3, and service metrics
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - START_TIME),
        "checks": {}
    }
    
    # Check MongoDB
    try:
        await db.client.admin.command('ping')
        health_status["checks"]["mongodb"] = {
            "status": "up",
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["mongodb"] = {
            "status": "down",
            "message": f"MongoDB connection failed: {str(e)}"
        }
        logger.error(f"Health check: MongoDB down - {e}")
    
    # Check S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION_V3
        )
        s3_client.head_bucket(Bucket=config.S3_BUCKET_V3)
        health_status["checks"]["s3"] = {
            "status": "up",
            "message": "S3 connection successful"
        }
    except ClientError as e:
        health_status["status"] = "degraded"
        health_status["checks"]["s3"] = {
            "status": "down",
            "message": f"S3 connection failed: {str(e)}"
        }
        logger.error(f"Health check: S3 down - {e}")
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["s3"] = {
            "status": "down",
            "message": str(e)
        }
    
    # Database counts (metrics)
    try:
        users_count = await db.users.count_documents({})
        parcels_count = await db.parcels.count_documents({})
        scans_count = await db.scans.count_documents({})
        
        health_status["metrics"] = {
            "total_users": users_count,
            "total_parcels": parcels_count,
            "total_scans": scans_count
        }
    except Exception as e:
        logger.error(f"Health check: Metrics failed - {e}")
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics
    Returns: Database stats, counts, and system info
    """
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - START_TIME),
            "database": {
                "users": await db.users.count_documents({}),
                "establishments": await db.establishments.count_documents({}),
                "parcels": await db.parcels.count_documents({}),
                "crops": await db.crops.count_documents({}),
                "scans": await db.scans.count_documents({}),
                "beta_requests": await db.beta_requests.count_documents({})
            },
            "beta_requests_status": {
                "pending": await db.beta_requests.count_documents({"status": "pending"}),
                "approved": await db.beta_requests.count_documents({"status": "approved"}),
                "rejected": await db.beta_requests.count_documents({"status": "rejected"})
            }
        }
        return metrics
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")
