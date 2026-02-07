from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.database import db
from app.core.notifications import email_notifier
from app.core import config
from datetime import datetime, timedelta
import secrets
import bcrypt
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


class PasswordResetRequest(BaseModel):
    identifier: str  # email or username


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/request", summary="Request password reset")
async def request_password_reset(data: PasswordResetRequest):
    identifier = (data.identifier or "").strip()
    if not identifier:
        raise HTTPException(status_code=400, detail="Identifiant requis")

    # Try to find user by email or username
    query = {"$or": [{"email": identifier.lower()}, {"username": identifier}]}
    user = await db["users"].find_one(query)

    # Always return success to avoid user enumeration
    if not user:
        return {"message": "Si ce compte existe, un e-mail a été envoyé."}

    # Determine email to send
    to_email = user.get("email") or (identifier if "@" in identifier else None)
    if not to_email:
        logger.warning("Password reset requested but no email available for user")
        return {"message": "Si ce compte existe, un e-mail a été envoyé."}

    # Create reset token (valid 1 hour)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    await db["password_reset_tokens"].insert_one({
        "user_id": user["_id"],
        "token": token,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "used": False
    })

    await email_notifier.send_password_reset_email(
        to_email=to_email,
        name=user.get("full_name") or user.get("username") or "",
        token=token,
        base_url=config.FRONTEND_BASE_URL,
        expires_at=expires_at.strftime("%Y-%m-%d %H:%M UTC")
    )

    return {"message": "Si ce compte existe, un e-mail a été envoyé."}


@router.post("/confirm", summary="Confirm password reset")
async def confirm_password_reset(data: PasswordResetConfirm):
    if len(data.new_password or "") < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")

    token_doc = await db["password_reset_tokens"].find_one({"token": data.token})
    if not token_doc:
        raise HTTPException(status_code=400, detail="Jeton invalide ou expiré")

    if token_doc.get("used"):
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")

    if datetime.utcnow() > token_doc.get("expires_at", datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Jeton expiré")

    hashed_password = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt())

    await db["users"].update_one(
        {"_id": token_doc["user_id"]},
        {"$set": {"password": hashed_password.decode("utf-8")}}
    )

    await db["password_reset_tokens"].update_one(
        {"_id": token_doc["_id"]},
        {"$set": {"used": True, "used_at": datetime.utcnow()}}
    )

    return {"message": "Mot de passe réinitialisé avec succès"}