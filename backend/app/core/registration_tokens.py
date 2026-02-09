import base64
import json
import os
import time
import secrets
import hashlib
import hmac
from typing import Dict
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False

from app.core import config

# KEY should be 32 bytes for AES-256
_registration_key = None
_hmac_key = None

if getattr(config, "REGISTRATION_SECRET_KEY", None):
    # expected as base64url or raw bytes string
    try:
        _registration_key = base64.urlsafe_b64decode(config.REGISTRATION_SECRET_KEY)
    except Exception:
        _registration_key = config.REGISTRATION_SECRET_KEY.encode("utf-8")
else:
    # fallback for dev/tests
    _registration_key = hashlib.sha256((config.JWT_SECRET_KEY or "test-secret").encode()).digest()

# HMAC key can reuse same secret for now
_hmac_key = hashlib.sha256((config.REFRESH_SECRET_KEY or config.JWT_SECRET_KEY or "test-refresh-secret").encode()).digest()


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_decode(s: str) -> bytes:
    # add padding
    rem = len(s) % 4
    if rem:
        s = s + ("=" * (4 - rem))
    return base64.urlsafe_b64decode(s)


def generate_registration_token(beta_request_id: int | str, email: str, ttl_seconds: int = 24 * 3600) -> str:
    """Generate token = header.payload.signature

    header: base64url(JSON)
    payload: AESGCM.encrypt(nonce, plaintext)
    signature: HMAC_SHA256(header + '.' + payload)
    """
    header = {
        "type": "beta_registration",
        "issued_at": int(time.time()),
        "expires_at": int(time.time()) + int(ttl_seconds),
        "version": 1
    }
    header_b = json.dumps(header, separators=(",", ":")).encode()
    header_b64 = _b64u(header_b).encode()

    nonce = secrets.token_bytes(12)  # 96-bit nonce for AESGCM

    payload = {
        "beta_request_id": str(beta_request_id),
        "email": email,
        "email_hash": hashlib.sha256(email.encode()).hexdigest(),
        "nonce": _b64u(nonce)
    }
    plaintext = json.dumps(payload, separators=(",", ":")).encode()

    if _HAS_CRYPTO:
        aesgcm = AESGCM(_registration_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        payload_b64 = _b64u(nonce + ciphertext).encode()
    else:
        # fallback: store plaintext directly (not secure - for dev/test environments)
        payload_b64 = _b64u(plaintext).encode()

    mac = hmac.new(_hmac_key, header_b64 + b"." + payload_b64, digestmod=hashlib.sha256).digest()
    sig_b64 = _b64u(mac).encode()

    token = b".".join([header_b64, payload_b64, sig_b64]).decode()
    return token


def validate_registration_token(token: str) -> Dict:
    """Validate token and return payload dict. Raises ValueError on invalid."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")
    header_b64, payload_b64, sig_b64 = parts

    header_raw = _b64u_decode(header_b64)
    header = json.loads(header_raw)

    expected_mac = hmac.new(_hmac_key, (header_b64 + "." + payload_b64).encode(), digestmod=hashlib.sha256).digest()
    sig = _b64u_decode(sig_b64)
    if not hmac.compare_digest(expected_mac, sig):
        raise ValueError("Invalid token signature")

    payload_raw = _b64u_decode(payload_b64)
    if _HAS_CRYPTO:
        # payload_raw contains nonce + ciphertext
        nonce = payload_raw[:12]
        ciphertext = payload_raw[12:]

        aesgcm = AESGCM(_registration_key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            raise ValueError("Decryption failed")
    else:
        plaintext = payload_raw

    payload = json.loads(plaintext)

    # check expiry
    if header.get("expires_at") and int(time.time()) > int(header["expires_at"]):
        raise ValueError("Token expired")

    return {"header": header, "payload": payload}
