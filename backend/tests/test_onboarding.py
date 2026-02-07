import pytest
from httpx import AsyncClient
from bson import ObjectId

@pytest.mark.asyncio
async def test_onboarding_status_default(client: AsyncClient, auth_headers):
    # New user should have onboarding_completed == False
    response = await client.get("/onboarding/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_completed"] is False

@pytest.mark.asyncio
async def test_onboarding_complete_creates_establishment(client: AsyncClient, auth_headers):
    payload = {
        "establishment_name": "Ferma Test",
        "address": "Str. Test 1",
        "siret": "12345678900012",
        "total_area_ha": 12.5
    }

    # Attempt should fail if phone not verified
    response = await client.post("/onboarding/complete", json=payload, headers=auth_headers)
    assert response.status_code == 400

    # Send verification code to the user's phone
    # Get user phone from DB
    from app.core.database import db
    user = await db["users"].find_one({"username": "test@vitiscan.com"})
    assert user is not None
    phone = user.get("phone")
    assert phone is None or isinstance(phone, (str, type(None)))

    # For test, set phone and then send code
    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"phone": "+40700123456"}})
    send_resp = await client.post("/send-verification-code", json={"phone": "+40700123456"})
    assert send_resp.status_code == 200

    # Retrieve the code from in-memory storage
    from app.routes import auth as auth_module
    code_data = auth_module.get_verification_code("+40700123456")
    assert code_data is not None
    code = code_data["code"]

    verify_resp = await client.post("/verify-phone-code", json={"phone": "+40700123456", "code": code})
    assert verify_resp.status_code == 200

    # Now completing onboarding should succeed
    response2 = await client.post("/onboarding/complete", json=payload, headers=auth_headers)
    assert response2.status_code == 201
    data2 = response2.json()
    assert "establishment_id" in data2

    # Test uploading a logo to the new establishment
    est_id = data2["establishment_id"]
    # Upload a small file
    files = {"file": ("logo.png", b"PNGDATA", "image/png")}
    upload_resp = await client.post(f"/establishments/{est_id}/logo", files=files, headers=auth_headers)
    assert upload_resp.status_code == 200
    up_data = upload_resp.json()
    assert "logo_url" in up_data

    # Check status now true
    status_resp = await client.get("/onboarding/status", headers=auth_headers)
    assert status_resp.status_code == 200
    assert status_resp.json().get("onboarding_completed") is True

    # Verify establishment exists
    from app.core.database import db
    est = await db["establishments"].find_one({"_id": ObjectId(data2["establishment_id"])})
    assert est is not None
    assert est["name"] == payload["establishment_name"]
