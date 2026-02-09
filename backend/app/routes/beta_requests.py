from fastapi import APIRouter, Depends, HTTPException, Request, Body
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from datetime import datetime, timedelta
from app.core.database import db
from app.routes.auth import get_current_admin_user, sms_notifier, normalize_phone, is_valid_phone, generate_verification_code, store_verification_code, get_verification_code
from app.core.notifications import telegram_notifier, email_notifier
from app.core.security import require_admin_roles
from app.core import config
from app.core.utils import validate_object_id, sanitize_error_message
import secrets
import logging
import bcrypt

logger = logging.getLogger(__name__)

router = APIRouter()


class BetaRequestCreate(BaseModel):
    email: EmailStr
    phone: str
    name: str
    farm_name: str


class BetaRequestResponse(BaseModel):
    id: str
    email: str
    phone: str
    name: str
    farm_name: str
    status: str
    created_at: str
    approved_at: str | None = None
    rejected_reason: str | None = None


class BetaRegistrationComplete(BaseModel):
    password: str
    verification_code: str | None = None  # For phone verification


@router.post("/beta-request", summary="Submit beta access request")
async def create_beta_request(data: BetaRequestCreate):
    """
    Public endpoint - anyone can request beta access
    Sends notification to admin via Telegram and Email
    """
    try:
        # Check if email already exists
        existing = await db["beta_requests"].find_one({"email": data.email})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="L'e-mail a déjà été enregistré. Vous serez contacté bientôt."
            )
        
        # Create beta request
        beta_request = {
            "email": data.email,
            "phone": data.phone,
            "name": data.name,
            "farm_name": data.farm_name,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "approved_at": None,
            "rejected_reason": None
        }
        
        result = await db["beta_requests"].insert_one(beta_request)
        request_id = str(result.inserted_id)
        
        # Send Telegram notification to admin
        await telegram_notifier.notify_beta_request(
            email=data.email,
            phone=data.phone,
            name=f"{data.name} - {data.farm_name}",
            request_id=request_id,
            farm_name=data.farm_name
        )
        
        logger.info(f"Beta request created: {request_id} for {data.email}")
        
        return {
            "message": "Votre demande a été soumise avec succès ! Vous serez contacté dans 48 heures.",
            "request_id": request_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating beta request: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


@router.get("/admin/beta-requests", response_model=list[BetaRequestResponse], summary="Get all beta requests")
async def get_beta_requests(
    status: str | None = None,
    admin: dict = Depends(get_current_admin_user)
):
    """
    Admin only - get all beta requests
    Optional filter by status: pending, approved, rejected
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        cursor = db["beta_requests"].find(query).sort("created_at", -1)
        requests = await cursor.to_list(length=None)
        
        result = []
        for req in requests:
            result.append({
                "id": str(req["_id"]),
                "email": req["email"],
                "phone": req["phone"],
                "name": req["name"],
                "farm_name": req.get("farm_name", ""),
                "status": req["status"],
                "created_at": req["created_at"].isoformat(),
                "approved_at": req.get("approved_at").isoformat() if req.get("approved_at") else None,
                "rejected_reason": req.get("rejected_reason")
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving beta requests: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


@router.put("/admin/beta-requests/{request_id}", summary="Admin action on beta request")
async def admin_update_beta_request(
    request_id: str,
    data: dict,
    request: Request,
    admin: dict = Depends(require_admin_roles("super_admin", "onboarding_admin"))
):
    """Unified admin endpoint to approve/reject/resend/update_notes on beta requests

    Expected body (JSON): {"action": "approve"|"reject"|"resend"|"update_notes", "reason": "...", "admin_notes": "...", "override": true}
    """
    try:
        action = data.get("action")
        if not action:
            raise HTTPException(status_code=400, detail="Action required")

        req_oid = validate_object_id(request_id, "request_id")
        beta_request = await db["beta_requests"].find_one({"_id": req_oid})
        if not beta_request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Capture admin context for audit
        admin_id = str(admin.get("_id") or admin.get("sub") or admin.get("id"))
        admin_email = admin.get("username") or admin.get("email")
        ip = request.client.host if request.client else "unknown"
        ua = request.headers.get("user-agent", "unknown")

        from app.routes.audit import log_audit_event

        # Approve
        if action == "approve":
            # Allow override only for super_admin
            override = bool(data.get("override", False))
            if beta_request.get("status") != "pending" and not (override and admin.get("role") == "super_admin"):
                raise HTTPException(status_code=400, detail=f"Request is already {beta_request.get('status')}")

            # Generate token
            from app.core import registration_tokens as rt
            token = rt.generate_registration_token(req_oid, beta_request["email"])
            header_payload = rt.validate_registration_token(token)
            payload = header_payload["payload"]
            nonce = payload.get("nonce")
            expires_at = datetime.utcfromtimestamp(header_payload["header"].get("expires_at"))

            # Invalidate existing pending tokens for this request
            await db["registration_tokens"].update_many({"beta_request_id": str(req_oid), "status": "pending"}, {"$set": {"status": "invalid", "invalidated_at": datetime.utcnow()}})

            # Update beta request
            await db["beta_requests"].update_one({"_id": req_oid}, {"$set": {"status": "approved", "approved_at": datetime.utcnow(), "token_expires_at": expires_at, "resend_count": 0, "last_resend_at": None}})

            # Save new token record
            await db["registration_tokens"].insert_one({"nonce": nonce, "beta_request_id": str(req_oid), "status": "pending", "created_at": datetime.utcnow(), "expires_at": expires_at})

            # Send email
            base_url = config.FRONTEND_BASE_URL
            await email_notifier.send_beta_approved_email(to_email=beta_request["email"], name=beta_request["name"], token=token, base_url=base_url)

            # Audit log
            await log_audit_event(user_id=f"admin:{admin_id}", action="beta_request.approve", outcome="success", resource_type="beta_request", resource_id=str(req_oid), details={"admin_email": admin_email, "ip": ip, "user_agent": ua})

            return {"message": "Request approved successfully", "registration_token": token}

        # Reject
        if action == "reject":
            reason = data.get("reason")
            admin_notes = data.get("admin_notes")
            allowed_reasons = {
                "incompatible": "Profil incompatibil cu versiunea beta",
                "capacity": "Capacitate limitată în programul beta",
                "already_client": "Deja client / deja pe platformă",
                "insufficient": "Informații insuficiente / incomplete",
                "other": "Alt motiv"
            }

            if not reason or reason not in allowed_reasons:
                raise HTTPException(status_code=400, detail="Invalid or missing reject reason")

            if reason == "other" and (not admin_notes or not admin_notes.strip()):
                raise HTTPException(status_code=400, detail="Admin notes required when reason is 'other'")

            # Allow override only for super_admin
            override = bool(data.get("override", False))
            if beta_request.get("status") != "pending" and not (override and admin.get("role") == "super_admin"):
                raise HTTPException(status_code=400, detail=f"Request is already {beta_request.get('status')}")

            rejected_text = allowed_reasons.get(reason)
            if reason == "other":
                rejected_text = f"Alt motiv: {admin_notes}"

            await db["beta_requests"].update_one({"_id": req_oid}, {"$set": {"status": "rejected", "rejected_reason": rejected_text, "admin_notes": admin_notes, "rejected_at": datetime.utcnow()}})

            # Send rejection email with reason
            await email_notifier.send_beta_rejected_email(to_email=beta_request["email"], name=beta_request["name"], reason=rejected_text, admin_notes=admin_notes)

            await log_audit_event(user_id=f"admin:{admin_id}", action="beta_request.reject", outcome="success", resource_type="beta_request", resource_id=str(req_oid), details={"reason": reason, "admin_notes": admin_notes, "admin_email": admin_email, "ip": ip, "user_agent": ua})

            return {"message": "Request rejected and email sent to user"}

        # Resend token
        if action == "resend":
            # Only allowed on approved and not yet completed requests
            if beta_request.get("status") != "approved":
                raise HTTPException(status_code=400, detail="Only approved requests can be resent")
            if beta_request.get("completed_at"):
                raise HTTPException(status_code=400, detail="User already registered")

            resend_count = int(beta_request.get("resend_count", 0))
            if resend_count >= 3:
                raise HTTPException(status_code=400, detail="Resend limit reached")

            # Invalidate existing pending tokens
            await db["registration_tokens"].update_many({"beta_request_id": str(req_oid), "status": "pending"}, {"$set": {"status": "invalid", "invalidated_at": datetime.utcnow()}})

            # Generate new token
            from app.core import registration_tokens as rt
            token = rt.generate_registration_token(req_oid, beta_request["email"])            
            header_payload = rt.validate_registration_token(token)
            expires_at = datetime.utcfromtimestamp(header_payload["header"].get("expires_at"))
            payload = header_payload["payload"]
            nonce = payload.get("nonce")

            # Insert token record
            await db["registration_tokens"].insert_one({"nonce": nonce, "beta_request_id": str(req_oid), "status": "pending", "created_at": datetime.utcnow(), "expires_at": expires_at})

            # Update counters
            await db["beta_requests"].update_one({"_id": req_oid}, {"$inc": {"resend_count": 1}, "$set": {"token_expires_at": expires_at, "last_resend_at": datetime.utcnow()}})

            # Send approval email with new token
            base_url = config.FRONTEND_BASE_URL
            await email_notifier.send_beta_approved_email(to_email=beta_request["email"], name=beta_request["name"], token=token, base_url=base_url)

            await log_audit_event(user_id=f"admin:{admin_id}", action="beta_request.resend_token", outcome="success", resource_type="beta_request", resource_id=str(req_oid), details={"admin_email": admin_email, "ip": ip, "user_agent": ua, "resend_count": resend_count + 1})

            return {"message": "Registration token resent and email sent", "registration_token": token}

        # Update notes
        if action == "update_notes":
            admin_notes = data.get("admin_notes")
            await db["beta_requests"].update_one({"_id": req_oid}, {"$set": {"admin_notes": admin_notes}})
            await log_audit_event(user_id=f"admin:{admin_id}", action="beta_request.update_notes", outcome="success", resource_type="beta_request", resource_id=str(req_oid), details={"admin_email": admin_email, "admin_notes": admin_notes, "ip": ip, "user_agent": ua})
            return {"message": "Admin notes updated"}

        raise HTTPException(status_code=400, detail="Unknown action")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing admin action on beta request: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))


@router.post("/admin/beta-requests/{request_id}/reject", summary="Reject beta request (legacy)")
async def reject_beta_request_legacy(
    request_id: str,
    request: Request,
    data: dict = Body(None),
    admin: dict = Depends(require_admin_roles("super_admin", "onboarding_admin"))
):
    # Delegate to unified handler
    body = {"action": "reject"}
    if data:
        body.update(data)
    return await admin_update_beta_request(request_id, body, request, admin)


@router.get("/beta-request/verify/{token}", summary="Verify beta registration token")
async def verify_beta_registration_token(token: str):
    """
    Public endpoint - verify if registration token is valid
    Returns basic user info for completing registration
    """
    try:
        # Validate cryptographic token
        from app.core import registration_tokens as rt
        validated = rt.validate_registration_token(token)
        payload = validated["payload"]
        beta_request_id = payload.get("beta_request_id")
        # Find beta request
        from bson import ObjectId
        req_oid = ObjectId(beta_request_id)
        beta_request = await db["beta_requests"].find_one({"_id": req_oid})

        if not beta_request or beta_request.get("status") != "approved":
            raise HTTPException(status_code=404, detail="Token invalid sau expirat")

        # check registration_tokens nonce state
        nonce = payload.get("nonce")
        token_doc = await db["registration_tokens"].find_one({"nonce": nonce})
        if not token_doc or token_doc.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Token expirat sau deja utilizat")

        return {
            "email": beta_request.get("email"),
            "full_name": beta_request.get("name"),
            "farm_name": beta_request.get("farm_name")
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying beta token: {str(e)}")
        raise HTTPException(status_code=500, detail="Eroare la verificarea token-ului")


@router.post("/beta-request/complete/{token}", summary="Complete beta registration")
async def complete_beta_registration(token: str, data: BetaRegistrationComplete):
    """
    Public endpoint - complete registration using approved token
    Step 1: Send verification code to phone
    Step 2: Verify code and create user account
    """
    try:
        beta_request = await db["beta_requests"].find_one({
            "registration_token": token,
            "status": "approved"
        })

        if not beta_request:
            raise HTTPException(status_code=404, detail="Token invalid sau expirat")

        token_expiry = beta_request.get("token_expiry")
        if token_expiry and datetime.utcnow() > token_expiry:
            raise HTTPException(status_code=400, detail="Token expirat")

        if beta_request.get("completed_at"):
            raise HTTPException(status_code=400, detail="Token deja utilizat")

        phone = beta_request.get("phone")
        if not phone:
            raise HTTPException(status_code=400, detail="Număr de telefon lipsă")

        normalized_phone = normalize_phone(phone)
        if not is_valid_phone(normalized_phone):
            raise HTTPException(status_code=400, detail="Număr de telefon invalid")

        # Check if user already exists
        existing_user = await db["users"].find_one({"username": beta_request.get("email")})
        if existing_user:
            raise HTTPException(status_code=400, detail="Contul există deja. Te poți autentifica.")

        # Step 1: If no verification code provided, send one
        if not data.verification_code:
            # Check if we already sent a code recently
            existing_code = get_verification_code(normalized_phone)
            if existing_code:
                # Return success but indicate code was already sent
                return {
                    "message": "Cod de verificare trimis anterior",
                    "requires_verification": True,
                    "phone": normalized_phone
                }

            # Generate and send verification code
            code = generate_verification_code()
            store_verification_code(normalized_phone, code)

            success = sms_notifier.send_verification_code(normalized_phone, code)
            if not success:
                logger.error(f"Failed to send verification SMS to {normalized_phone}")
                raise HTTPException(status_code=500, detail="Eroare la trimiterea codului SMS")

            logger.info(f"Verification code sent to {normalized_phone} for beta registration")
            return {
                "message": "Cod de verificare trimis pe SMS",
                "requires_verification": True,
                "phone": normalized_phone
            }

        # Step 2: Verify the code
        stored_data = get_verification_code(normalized_phone)
        if not stored_data or stored_data['code'] != data.verification_code:
            raise HTTPException(status_code=400, detail="Cod de verificare invalid sau expirat")

        # Code is valid - remove it from storage
        from app.routes.auth import verification_codes
        if normalized_phone in verification_codes:
            del verification_codes[normalized_phone]

        # Create user
        hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
        user = {
            "username": beta_request.get("email"),
            "password": hashed_password.decode("utf-8"),
            "role": "user",
            "language": "ro",
            "full_name": beta_request.get("name"),
            "phone": normalized_phone,
            "email": beta_request.get("email"),
            "created_at": datetime.utcnow()
        }

        result = await db["users"].insert_one(user)

        # Mark beta request completed
        await db["beta_requests"].update_one(
            {"_id": beta_request["_id"]},
            {"$set": {
                "completed_at": datetime.utcnow(),
                "user_id": str(result.inserted_id)
            }}
        )

        logger.info(f"Beta registration completed for {beta_request.get('email')} (ID: {result.inserted_id})")
        return {
            "message": "Cont creat cu succes!",
            "user_id": str(result.inserted_id),
            "requires_verification": False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing beta registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Eroare la finalizarea contului")
