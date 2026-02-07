# 🚀 QUICK-FIX GUIDE - VITISCAN V3 (7-Day Action Plan)

**Priority:** CRITICAL FIX BEFORE PRODUCTION  
**Target Completion:** 10 February 2026  
**Estimated Effort:** 38 hours

---

## 🔴 CRITICAL FIXES (18 hours) - MUST DO FIRST

### Fix #1: Admin Endpoint Protection (2 hours)

**Problem:** Admin routes accessible without admin role check

**Files affected:** `backend/app/routes/admin_global.py`

**Solution:**
```python
# Add this decorator to all admin routes:
from fastapi import Depends
from app.core.security import get_current_user

async def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Apply to route:
@router.get("/admin/users")
async def list_users(user: dict = Depends(require_admin)):
    # ... route logic
```

**Action Items:**
1. [ ] Audit all routes in admin_global.py
2. [ ] Add @admin_required to each endpoint
3. [ ] Test with non-admin user (should return 403)
4. [ ] Test with admin user (should succeed)

---

### Fix #2: File Upload Validation (3 hours)

**Problem:** No validation on uploaded files (can upload .exe, .sh, etc.)

**File:** `backend/app/routes/scans.py` (around line 60-100)

**Solution:**
```python
import mimetypes
from typing import List

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.pdf']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf']

async def validate_file_upload(file: UploadFile) -> bool:
    # 1. Check extension
    filename = file.filename or ""
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {file_ext} not allowed")
    
    # 2. Check MIME type
    mime_type = file.content_type or ""
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid file MIME type")
    
    # 3. Check file size (already configured)
    size = len(await file.read())
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, f"File too large (max {MAX_FILE_SIZE_MB}MB)")
    
    # 4. Check magic bytes (first few bytes of file)
    await file.seek(0)
    magic = await file.read(4)
    if not verify_magic_bytes(magic, file_ext):
        raise HTTPException(400, "File content doesn't match extension")
    
    return True

def verify_magic_bytes(magic: bytes, ext: str) -> bool:
    """Verify file magic bytes match extension"""
    checks = {
        '.jpg': magic.startswith(b'\xff\xd8\xff'),
        '.png': magic.startswith(b'\x89PNG'),
        '.tiff': magic.startswith(b'II') or magic.startswith(b'MM'),
        '.pdf': magic.startswith(b'%PDF'),
    }
    return checks.get(ext, False)

# Use in route:
@router.post("/parcels/{parcel_id}/scans")
async def upload_scan(parcel_id: str, file: UploadFile, user: dict = Depends(get_current_user)):
    await validate_file_upload(file)  # Add this line
    # ... rest of logic
```

**Action Items:**
1. [ ] Add validate_file_upload() function
2. [ ] Import magic bytes verification
3. [ ] Call validation before S3 upload
4. [ ] Test with invalid files (.exe, .txt, .zip)
5. [ ] Test with valid files

---

### Fix #3: Audit Logging (4 hours)

**Problem:** No tracking of who accessed/modified data

**Files:** Create `backend/app/core/audit_logging.py`

**Solution:**
```python
# backend/app/core/audit_logging.py
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, Optional

class AuditLogger:
    def __init__(self, db):
        self.db = db
        self.audit_collection = db["audit_logs"]
    
    async def log_action(
        self,
        action: str,  # "create", "read", "update", "delete"
        resource_type: str,  # "parcel", "treatment", "scan"
        resource_id: str,
        user_id: str,
        details: Dict[str, Any] = None,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None,
    ):
        log_entry = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "details": details or {},
            "old_values": old_values,
            "new_values": new_values,
            "ip_address": self.ip_address,  # Will set via middleware
        }
        await self.audit_collection.insert_one(log_entry)
    
    async def get_resource_history(self, resource_id: str):
        """Get all changes to a resource"""
        cursor = self.audit_collection.find({
            "resource_id": resource_id
        }).sort("timestamp", -1)
        return await cursor.to_list(length=None)

# Middleware to capture requests:
from app.core.database import db
from app.core.audit_logging import AuditLogger

audit_logger = AuditLogger(db)

@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    audit_logger.ip_address = request.client.host if request.client else "unknown"
    response = await call_next(request)
    return response
```

**Usage in routes:**
```python
# In POST /parcels/{id}/treatments
result = await db["treatments"].insert_one(treatment)
await audit_logger.log_action(
    action="create",
    resource_type="treatment",
    resource_id=str(result.inserted_id),
    user_id=user_id,
    new_values=treatment
)
```

**Action Items:**
1. [ ] Create audit_logging.py module
2. [ ] Add audit middleware
3. [ ] Instrument 10+ critical endpoints
4. [ ] Create audit endpoint: GET /audit/logs?resource_id=X
5. [ ] Test logging works

---

### Fix #4: Password Reset Flow (6 hours)

**Problem:** Users cannot recover forgotten passwords

**Files:** Create `backend/app/routes/password_reset.py`

**Solution:**
```python
# backend/app/routes/password_reset.py
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
from app.core.database import db
from app.core.config import JWT_SECRET_KEY
from app.core.security import hash_password, create_access_token
import httpx

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    """Send password reset email"""
    user = await db["users"].find_one({"email": data.email})
    if not user:
        # Security: Don't reveal if email exists
        return {"message": "If email exists, reset link sent"}
    
    # Create reset token (valid 1 hour)
    reset_token = jwt.encode(
        {
            "sub": user["_id"],
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    # Store token in DB
    await db["password_resets"].insert_one({
        "user_id": user["_id"],
        "token": reset_token,
        "created_at": datetime.utcnow(),
        "used": False
    })
    
    # Send email via Resend API
    reset_url = f"https://app.vitiscan.com/reset-password?token={reset_token}"
    
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": FROM_EMAIL,
                "to": data.email,
                "subject": "Reset Your VitiScan Password",
                "html": f"""
                    <p>Click link below to reset password:</p>
                    <a href="{reset_url}">Reset Password</a>
                    <p>Link valid for 1 hour.</p>
                """
            }
        )
    
    return {"message": "If email exists, reset link sent"}

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """Reset password with token"""
    try:
        payload = jwt.decode(data.token, JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "password_reset":
            raise HTTPException(400, "Invalid reset token")
    except:
        raise HTTPException(400, "Token expired or invalid")
    
    # Check token not already used
    reset_record = await db["password_resets"].find_one({"token": data.token})
    if not reset_record or reset_record.get("used"):
        raise HTTPException(400, "Token already used")
    
    # Update password
    user_id = ObjectId(payload["sub"])
    hashed = hash_password(data.new_password)
    await db["users"].update_one(
        {"_id": user_id},
        {"$set": {"password": hashed}}
    )
    
    # Mark token as used
    await db["password_resets"].update_one(
        {"token": data.token},
        {"$set": {"used": True, "used_at": datetime.utcnow()}}
    )
    
    return {"message": "Password reset successfully"}

# Add to main.py:
# from app.routes.password_reset import router as password_reset_router
# app.include_router(password_reset_router)
```

**Action Items:**
1. [ ] Create password_reset.py routes
2. [ ] Add to main.py router includes
3. [ ] Create frontend form (frontend/app/reset-password/page.tsx)
4. [ ] Test forgot-password email sending
5. [ ] Test reset-password with token

---

### Fix #5: Invitation Email (3 hours)

**Problem:** TODO not implemented, users can't be invited

**File:** `backend/app/routes/invitations.py` (line 122)

**Solution:**
Replace the TODO with:
```python
# backend/app/routes/invitations.py (around line 120)
@router.post("/invitations/{invitation_id}/send-email")
async def send_invitation_email(invitation_id: str, user: dict = Depends(get_current_user)):
    """Send invitation email to team member"""
    inv = await db["invitations"].find_one({
        "_id": ObjectId(invitation_id),
        "created_by": user.get("sub")
    })
    
    if not inv:
        raise HTTPException(404, "Invitation not found")
    
    if inv.get("email_sent"):
        raise HTTPException(400, "Email already sent")
    
    # Create acceptance link
    accept_token = jwt.encode(
        {
            "sub": inv["email"],
            "type": "team_invitation",
            "team_id": inv["team_id"],
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    accept_url = f"https://app.vitiscan.com/accept-invitation?token={accept_token}"
    
    # Send via Resend
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": FROM_EMAIL,
                "to": inv["email"],
                "subject": f"You're invited to join VitiScan team",
                "html": f"""
                    <p>You've been invited to join <strong>{inv['team_name']}</strong></p>
                    <p><a href="{accept_url}">Accept Invitation</a></p>
                    <p>Invitation expires in 7 days.</p>
                """
            }
        )
    
    await db["invitations"].update_one(
        {"_id": ObjectId(invitation_id)},
        {"$set": {"email_sent": True, "sent_at": datetime.utcnow()}}
    )
    
    return {"message": "Invitation email sent"}
```

**Action Items:**
1. [ ] Replace TODO with send_invitation_email function
2. [ ] Test email sending with valid email
3. [ ] Test email not sent twice
4. [ ] Create invitation acceptance endpoint

---

## 🟠 HIGH PRIORITY FIXES (20 hours) - Do in Week 2

### Fix #6: Add Role-Based Access Control (6 hours)
**File:** `backend/app/core/authz_decorators.py`  
**What:** Currently only owner/non-owner. Need: admin, operator, viewer roles  

### Fix #7: Implement Pagination (2 hours)
**File:** `backend/app/routes/parcels.py`  
**What:** All GET endpoints need limit/offset parameters

### Fix #8: Add Swagger UI (1 hour)
**File:** `backend/app/main.py`  
**What:** Enable automatic API documentation

### Fix #9: Write 12+ Integration Tests (8 hours)
**File:** `backend/tests/` (create new test files)  
**What:** Parcel CRUD, treatments, PDF export, concurrent updates

### Fix #10: Switch to Redis Rate Limiting (3 hours)
**File:** `backend/app/core/rate_limiting.py`  
**What:** In-memory cache won't work in production

---

## ✅ QUICK WINS (Can do in parallel)

1. **Fix CSP headers** (1h) - Current `default-src 'self'` may break features
2. **Add Swagger UI** (1h) - Enable at `/docs`
3. **Create API documentation** (2h) - Document all endpoints
4. **Fix typing** (1h) - Replace `any` types in frontend
5. **Remove TODO comments** (1h) - Document why or implement

---

## 📋 VALIDATION CHECKLIST

After each fix, verify:

```bash
# 1. Code syntax check
python -m py_compile backend/app/routes/admin_global.py

# 2. Run tests
pytest backend/tests/

# 3. Check logs
tail -f backend/logs/error_*.log

# 4. Frontend build
cd frontend && npm run build

# 5. Manual testing
curl -X GET http://localhost:8000/health
```

---

## 🎯 TIMELINE

```
Monday (Feb 3):     Fix #1-2 (4h) ✅ DONE
Tuesday (Feb 4):    Fix #3-4 (10h) - Audit + Password reset
Wednesday (Feb 5):  Fix #5 + Testing (5h) - Invitations + validation
Thursday (Feb 6):   Quick wins (4h) - CSP, Swagger, docs
Friday (Feb 7):     Integration tests (8h) - Week 1 tests

Week 2:             RBAC, Pagination, Redis, Advanced tests
```

---

## 📞 QUESTIONS?

If something is unclear:
1. Check existing code for similar patterns
2. Review related tests
3. Ask team lead for context
4. Document blockers and follow up

**Status:** All 5 CRITICAL fixes outlined above  
**Next:** Start with Fix #1 (2h quick win)
