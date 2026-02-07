"""
AWS S3 Storage Utilities for VitiScan v3

This module provides functions for uploading and downloading files to/from AWS S3.
Files are stored in S3 while metadata is kept in MongoDB.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
import logging
from datetime import datetime
import uuid
from . import config

logger = logging.getLogger(__name__)

class S3Storage:
    """S3 storage manager for scan files"""
    
    def __init__(self):
        """Initialize S3 clients for different regions"""
        # Client for main bucket (Paris - eu-west-3)
        self.s3_v3 = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION_V3
        )
        self.bucket_v3 = config.S3_BUCKET_V3
        
        # Client for AI images bucket (Stockholm - eu-north-1)
        self.s3_ai_v3 = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION_AI_V3
        )
        self.bucket_ai_v3 = config.S3_BUCKET_AI_IMAGES_V3
        
        logger.info(f"S3Storage initialized with buckets: {self.bucket_v3}, {self.bucket_ai_v3}")
    
    def generate_s3_key(self, user_id: str, parcel_id: str, filename: str) -> str:
        """
        Generate a unique S3 key for a file
        
        Format: scans/{user_id}/{parcel_id}/{timestamp}_{uuid}_{filename}
        
        Args:
            user_id: User ID from JWT
            parcel_id: Parcel ID
            filename: Original filename
            
        Returns:
            S3 key (path) for the file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = filename.replace(" ", "_")
        
        return f"scans/{user_id}/{parcel_id}/{timestamp}_{unique_id}_{safe_filename}"
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        parcel_id: str,
        bucket_type: str = "main"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a file to S3
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type
            user_id: User ID
            parcel_id: Parcel ID
            bucket_type: "main" or "ai" for different buckets
            
        Returns:
            Tuple of (success, s3_key, error_message)
        """
        try:
            s3_key = self.generate_s3_key(user_id, parcel_id, filename)
            
            # Select bucket and client
            if bucket_type == "ai":
                s3_client = self.s3_ai_v3
                bucket = self.bucket_ai_v3
            else:
                s3_client = self.s3_v3
                bucket = self.bucket_v3
            
            # Upload to S3
            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'user_id': user_id,
                    'parcel_id': parcel_id,
                    'original_filename': filename
                }
            )
            
            logger.info(f"File uploaded to S3: {bucket}/{s3_key}")
            return True, s3_key, None
            
        except ClientError as e:
            error_msg = f"S3 upload error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    async def download_file(
        self,
        s3_key: str,
        bucket_type: str = "main"
    ) -> Tuple[bool, Optional[bytes], Optional[str], Optional[str]]:
        """
        Download a file from S3
        
        Args:
            s3_key: S3 key (path) of the file
            bucket_type: "main" or "ai" for different buckets
            
        Returns:
            Tuple of (success, file_content, content_type, error_message)
        """
        try:
            # Select bucket and client
            if bucket_type == "ai":
                s3_client = self.s3_ai_v3
                bucket = self.bucket_ai_v3
            else:
                s3_client = self.s3_v3
                bucket = self.bucket_v3
            
            # Download from S3
            response = s3_client.get_object(Bucket=bucket, Key=s3_key)
            file_content = response['Body'].read()
            content_type = response.get('ContentType', 'application/octet-stream')
            
            logger.info(f"File downloaded from S3: {bucket}/{s3_key}")
            return True, file_content, content_type, None
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                error_msg = "File not found in S3"
            else:
                error_msg = f"S3 download error: {str(e)}"
            logger.error(error_msg)
            return False, None, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            logger.error(error_msg)
            return False, None, None, error_msg
    
    async def delete_file(
        self,
        s3_key: str,
        bucket_type: str = "main"
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 key (path) of the file
            bucket_type: "main" or "ai" for different buckets
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Select bucket and client
            if bucket_type == "ai":
                s3_client = self.s3_ai_v3
                bucket = self.bucket_ai_v3
            else:
                s3_client = self.s3_v3
                bucket = self.bucket_v3
            
            # Delete from S3
            s3_client.delete_object(Bucket=bucket, Key=s3_key)
            
            logger.info(f"File deleted from S3: {bucket}/{s3_key}")
            return True, None
            
        except ClientError as e:
            error_msg = f"S3 delete error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during delete: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


# Global instance
s3_storage = S3Storage()
