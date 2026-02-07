"""
Tests for scan upload endpoint
"""
import pytest
from httpx import AsyncClient
from app.core.database import db
import app.routes.scans as scans_routes


def _tenant_headers(auth_headers: dict, establishment_id: str) -> dict:
    return {**auth_headers, "X-Tenant-Id": f"est:{establishment_id}"}


def _coords():
    return [[[24.5, 45.5], [24.6, 45.5], [24.6, 45.6], [24.5, 45.6], [24.5, 45.5]]]


async def _create_establishment_and_parcel(client: AsyncClient, auth_headers: dict) -> tuple[str, dict]:
    establishment = {
        "name": "Test Farm",
        "siret": "123456",
        "address": "Test Location",
        "surface_ha": 10.5,
    }
    est_response = await client.post("/establishments", json=establishment, headers=auth_headers)
    est_id = est_response.json()["id"]
    tenant_headers = _tenant_headers(auth_headers, est_id)

    parcel = {
        "name": "Test Parcel",
        "establishment_id": est_id,
        "area_ha": 2.3,
        "crop_type": "ViÈ›Äƒ de vie",
        "coordinates": _coords(),
    }
    parcel_response = await client.post("/parcels", json=parcel, headers=tenant_headers)
    return parcel_response.json()["id"], tenant_headers


@pytest.mark.asyncio
async def test_upload_scan_success(client: AsyncClient, auth_headers, monkeypatch):
    async def fake_upload_file(*args, **kwargs):
        return True, "scans/test/key.jpg", None

    monkeypatch.setattr(scans_routes.s3_storage, "upload_file", fake_upload_file)

    parcel_id, tenant_headers = await _create_establishment_and_parcel(client, auth_headers)

    files = {
        "file": ("test.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", "image/jpeg"),
    }

    response = await client.post(f"/scans/{parcel_id}/upload", files=files, headers=tenant_headers)
    assert response.status_code == 201
    data = response.json()
    assert "scan_id" in data

    await db["scans"].delete_many({"parcel_id": parcel_id})


@pytest.mark.asyncio
async def test_upload_scan_invalid_file(client: AsyncClient, auth_headers):
    parcel_id, tenant_headers = await _create_establishment_and_parcel(client, auth_headers)

    files = {
        "file": ("malware.exe", b"MZ\x00\x00\x00\x00", "application/octet-stream"),
    }

    response = await client.post(f"/scans/{parcel_id}/upload", files=files, headers=tenant_headers)
    assert response.status_code == 400
