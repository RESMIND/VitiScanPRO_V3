"""
Rate limiting and quota management
Prevents abuse and supports tiered pricing plans
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request, status
from app.core.database import get_db

# In-memory rate limiting (for production, use Redis)
rate_limit_cache = {}

class RateLimiter:
    """Rate limiting utility"""
    
    @staticmethod
    def check_rate_limit(
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, False if exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in rate_limit_cache:
            rate_limit_cache[key] = []
        
        # Clean old requests
        rate_limit_cache[key] = [
            timestamp for timestamp in rate_limit_cache[key]
            if timestamp > window_start
        ]
        
        # Check limit
        if len(rate_limit_cache[key]) >= max_requests:
            return False
        
        # Add current request
        rate_limit_cache[key].append(now)
        return True
    
    @staticmethod
    def get_remaining(key: str, max_requests: int = 100, window_seconds: int = 60) -> int:
        """Get remaining requests in current window"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in rate_limit_cache:
            return max_requests
        
        # Clean old requests
        rate_limit_cache[key] = [
            timestamp for timestamp in rate_limit_cache[key]
            if timestamp > window_start
        ]
        
        return max(0, max_requests - len(rate_limit_cache[key]))


class QuotaManager:
    """Quota management for tiered plans"""
    
    PLANS = {
        'free': {
            'parcels': 3,
            'scans_per_month': 10,
            'storage_mb': 100,
            'team_members': 1,
            'api_calls_per_day': 100
        },
        'pro': {
            'parcels': 50,
            'scans_per_month': 500,
            'storage_mb': 5000,
            'team_members': 10,
            'api_calls_per_day': 5000
        },
        'enterprise': {
            'parcels': -1,  # unlimited
            'scans_per_month': -1,
            'storage_mb': -1,
            'team_members': -1,
            'api_calls_per_day': -1
        }
    }
    
    @staticmethod
    def get_user_plan(user_id: str, db) -> str:
        """Get user's current plan"""
        user = db.users.find_one({'id': user_id})
        return user.get('plan', 'free') if user else 'free'
    
    @staticmethod
    def get_plan_limits(plan: str) -> dict:
        """Get limits for a plan"""
        return QuotaManager.PLANS.get(plan, QuotaManager.PLANS['free'])
    
    @staticmethod
    def check_quota(
        user_id: str,
        resource_type: str,
        db,
        increment: int = 1
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user has quota for resource
        Returns (allowed: bool, error_message: Optional[str])
        """
        plan = QuotaManager.get_user_plan(user_id, db)
        limits = QuotaManager.get_plan_limits(plan)
        
        # Get current usage
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if resource_type == 'parcels':
            current = db.parcels.count_documents({'user_id': user_id})
            limit = limits['parcels']
            
            if limit != -1 and current >= limit:
                return False, f"Parcel limit reached. Upgrade to Pro for more parcels. (Current: {current}/{limit})"
        
        elif resource_type == 'scans':
            current = db.scans.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': month_start.isoformat()}
            })
            limit = limits['scans_per_month']
            
            if limit != -1 and current >= limit:
                return False, f"Monthly scan limit reached. Upgrade to Pro for more scans. (Current: {current}/{limit})"
        
        elif resource_type == 'team_members':
            current = db.establishment_members.count_documents({
                'invited_by': user_id,
                'is_active': True
            })
            limit = limits['team_members']
            
            if limit != -1 and current >= limit:
                return False, f"Team member limit reached. Upgrade to Pro to invite more members. (Current: {current}/{limit})"
        
        elif resource_type == 'storage':
            # Calculate total storage used
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {'_id': None, 'total': {'$sum': '$file_size_bytes'}}}
            ]
            result = list(db.scans.aggregate(pipeline))
            current_bytes = result[0]['total'] if result else 0
            current_mb = current_bytes / (1024 * 1024)
            limit = limits['storage_mb']
            
            if limit != -1 and current_mb >= limit:
                return False, f"Storage limit reached. Upgrade to Pro for more storage. (Current: {current_mb:.1f}MB/{limit}MB)"
        
        return True, None
    
    @staticmethod
    def get_usage_stats(user_id: str, db) -> dict:
        """Get current usage statistics for user"""
        plan = QuotaManager.get_user_plan(user_id, db)
        limits = QuotaManager.get_plan_limits(plan)
        
        # Current month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get counts
        parcels_count = db.parcels.count_documents({'user_id': user_id})
        scans_month = db.scans.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': month_start.isoformat()}
        })
        members_count = db.establishment_members.count_documents({
            'invited_by': user_id,
            'is_active': True
        })
        
        # Storage
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {'_id': None, 'total': {'$sum': '$file_size_bytes'}}}
        ]
        result = list(db.scans.aggregate(pipeline))
        storage_bytes = result[0]['total'] if result else 0
        storage_mb = storage_bytes / (1024 * 1024)
        
        return {
            'plan': plan,
            'usage': {
                'parcels': {
                    'current': parcels_count,
                    'limit': limits['parcels'],
                    'unlimited': limits['parcels'] == -1
                },
                'scans_this_month': {
                    'current': scans_month,
                    'limit': limits['scans_per_month'],
                    'unlimited': limits['scans_per_month'] == -1
                },
                'team_members': {
                    'current': members_count,
                    'limit': limits['team_members'],
                    'unlimited': limits['team_members'] == -1
                },
                'storage_mb': {
                    'current': round(storage_mb, 2),
                    'limit': limits['storage_mb'],
                    'unlimited': limits['storage_mb'] == -1
                }
            }
        }


async def rate_limit_middleware(request: Request, call_next):
    """Middleware for global rate limiting"""
    
    # Get user identifier (IP or user_id)
    user_id = getattr(request.state, 'user_id', None)
    ip = request.client.host if request.client else 'unknown'
    key = f"rate_limit:{user_id or ip}"
    
    # Check rate limit (100 requests per minute)
    if not RateLimiter.check_rate_limit(key, max_requests=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Add rate limit headers
    response = await call_next(request)
    remaining = RateLimiter.get_remaining(key, max_requests=100, window_seconds=60)
    response.headers['X-RateLimit-Remaining'] = str(remaining)
    response.headers['X-RateLimit-Limit'] = '100'
    
    return response


def require_quota(resource_type: str):
    """Dependency to check quota before action"""
    async def quota_checker(request: Request, db = get_db()):
        user_id = getattr(request.state, 'user_id', None)
        if not user_id:
            return  # Let auth middleware handle
        
        allowed, error_msg = QuotaManager.check_quota(user_id, resource_type, db)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=error_msg
            )
    
    return quota_checker
