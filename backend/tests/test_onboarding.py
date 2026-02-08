import pytest
from httpx import AsyncClient
from bson import ObjectId

@pytest.mark.asyncio
async def test_onboarding_status_default(client: AsyncClient, auth_header):
    # New user should have onboarding_completed == False (initial state)
    response = await client.get("/onboarding/status", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_completed"] is False

@pytest.mark.asyncio
async def test_onboarding_complete_creates_establishment(client: AsyncClient, auth_header, test_user):
    payload = {
        "establishment_name": "Ferma Test",
        "address": "Str. Test 1",
        "siret": "12345678900012",
        "total_area_ha": 12.5
    }

    # Because our CI test user is pre-marked as phone_verified, onboarding should succeed immediately
    response = await client.post("/onboarding/complete", json=payload, headers=auth_header)
    assert response.status_code == 201
    data2 = response.json()
    assert "establishment_id" in data2

    # Test uploading a logo to the new establishment
    est_id = data2["establishment_id"]
    # Upload a small file
    files = {"file": ("logo.png", b"PNGDATA", "image/png")}
    upload_resp = await client.post(f"/establishments/{est_id}/logo", files=files, headers=auth_header)
    assert upload_resp.status_code == 200
    up_data = upload_resp.json()
    assert "logo_url" in up_data

    # Check status now true
    status_resp = await client.get("/onboarding/status", headers=auth_header)
    assert status_resp.status_code == 200
    assert status_resp.json().get("onboarding_completed") is True

    # Verify establishment exists
    from app.core.database import db
    est = await db["establishments"].find_one({"_id": ObjectId(data2["establishment_id"])})
    assert est is not None
    assert est["name"] == payload["establishment_name"]
