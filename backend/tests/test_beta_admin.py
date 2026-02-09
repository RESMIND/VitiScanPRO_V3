#!/usr/bin/env python3
"""Tests for admin beta requests management"""
import pytest
import bcrypt
from app.core.database import db
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
async def create_user_with_role(role: str, username: str = None, password: str = "AdminPass123!"):
    username = username or f"{role}@vitiscan.test"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db["users"].insert_one({"username": username, "password": hashed, "role": role, "language": "en", "created_at": datetime.utcnow()})
    return {"username": username, "password": password}

@pytest.mark.asyncio
async def get_auth_header(client: AsyncClient, creds: dict):
    resp = await client.post("/login", json={"username": creds["username"], "password": creds["password"]})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_onboarding_admin_can_approve_and_resend(client: AsyncClient):
    # Create beta request
    resp = await client.post("/beta-request", json={"email": "foo@example.com", "phone": "+33612345678", "name": "Foo Bar", "farm_name": "Test Winery"})
    assert resp.status_code == 200
    request_id = resp.json()["request_id"]

    # Create onboarding_admin user
    creds = await create_user_with_role("onboarding_admin")
    headers = await get_auth_header(client, creds)

    # Approve
    approve_resp = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "approve"}, headers=headers)
    assert approve_resp.status_code == 200
    assert "registration_token" in approve_resp.json()

    # DB checks
    req_doc = await db["beta_requests"].find_one({"_id": __import__('bson').ObjectId(request_id)})
    assert req_doc["status"] == "approved"

    tokens = await db["registration_tokens"].find({"beta_request_id": request_id}).to_list(length=10)
    assert len(tokens) >= 1

    # Resend (first)
    resend_resp = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "resend"}, headers=headers)
    assert resend_resp.status_code == 200

    req_doc = await db["beta_requests"].find_one({"_id": __import__('bson').ObjectId(request_id)})
    assert req_doc.get("resend_count", 0) == 1

    # Resend until limit
    await client.put(f"/admin/beta-requests/{request_id}", json={"action": "resend"}, headers=headers)
    second_last = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "resend"}, headers=headers)
    assert second_last.status_code == 200
    # Fourth resend should fail (limit reached)
    fourth = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "resend"}, headers=headers)
    assert fourth.status_code == 400


@pytest.mark.asyncio
async def test_reject_requires_admin_notes_for_other(client: AsyncClient):
    resp = await client.post("/beta-request", json={"email": "bar@example.com", "phone": "+33623456789", "name": "Bar", "farm_name": "Domaine"})
    assert resp.status_code == 200
    request_id = resp.json()["request_id"]

    creds = await create_user_with_role("onboarding_admin", username="onboard2@vitiscan.test")
    headers = await get_auth_header(client, creds)

    # Attempt reject with "other" reason but missing notes
    r = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "reject", "reason": "other"}, headers=headers)
    assert r.status_code == 400

    # Now provide notes
    r2 = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "reject", "reason": "other", "admin_notes": "Test note details"}, headers=headers)
    assert r2.status_code == 200

    req_doc = await db["beta_requests"].find_one({"_id": __import__('bson').ObjectId(request_id)})
    assert req_doc["status"] == "rejected"
    assert "Alt motiv" in req_doc["rejected_reason"]


@pytest.mark.asyncio
async def test_super_admin_can_override(client: AsyncClient):
    resp = await client.post("/beta-request", json={"email": "baz@example.com", "phone": "+33634567890", "name": "Baz", "farm_name": "Baz Farm"})
    assert resp.status_code == 200
    request_id = resp.json()["request_id"]

    # Approve with onboarding_admin
    creds = await create_user_with_role("onboarding_admin", username="onboard3@vitiscan.test")
    headers = await get_auth_header(client, creds)
    r = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "approve"}, headers=headers)
    assert r.status_code == 200

    # Now super_admin can override and reject
    super_creds = await create_user_with_role("super_admin", username="super@vitiscan.test")
    super_headers = await get_auth_header(client, super_creds)
    r2 = await client.put(f"/admin/beta-requests/{request_id}", json={"action": "reject", "reason": "capacity", "override": True}, headers=super_headers)
    assert r2.status_code == 200

    req_doc = await db["beta_requests"].find_one({"_id": __import__('bson').ObjectId(request_id)})
    assert req_doc["status"] == "rejected"