"""
Tests for parcels CRUD operations
"""
import pytest
from httpx import AsyncClient


def _tenant_headers(auth_headers: dict, establishment_id: str) -> dict:
    return {**auth_headers, "X-Tenant-Id": f"est:{establishment_id}"}


def _coords():
    return [[[24.5, 45.5], [24.6, 45.5], [24.6, 45.6], [24.5, 45.6], [24.5, 45.5]]]


@pytest.mark.asyncio
async def test_create_parcel(client: AsyncClient, auth_headers):
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
    response = await client.post("/parcels", json=parcel, headers=tenant_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == parcel["name"]
    assert data["area_ha"] == parcel["area_ha"]


@pytest.mark.asyncio
async def test_get_parcels(client: AsyncClient, auth_headers):
    establishment = {
        "name": "Test Farm",
        "siret": "123456",
        "address": "Test Location",
        "surface_ha": 10.5,
    }
    est_response = await client.post("/establishments", json=establishment, headers=auth_headers)
    est_id = est_response.json()["id"]
    tenant_headers = _tenant_headers(auth_headers, est_id)

    response = await client.get(f"/parcels/by-establishment/{est_id}", headers=tenant_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_parcel_by_id(client: AsyncClient, auth_headers):
    establishment = {"name": "Farm", "siret": "123456", "address": "Location", "surface_ha": 5}
    est_response = await client.post("/establishments", json=establishment, headers=auth_headers)
    est_id = est_response.json()["id"]
    tenant_headers = _tenant_headers(auth_headers, est_id)

    parcel = {
        "name": "Parcel",
        "establishment_id": est_id,
        "area_ha": 1.5,
        "crop_type": "ViÈ›Äƒ de vie",
        "coordinates": _coords(),
    }
    create_response = await client.post("/parcels", json=parcel, headers=tenant_headers)
    parcel_id = create_response.json()["id"]

    response = await client.get(f"/parcels/by-establishment/{est_id}", headers=tenant_headers)
    assert response.status_code == 200
    parcels = response.json()
    assert any(p["id"] == parcel_id for p in parcels)


@pytest.mark.asyncio
async def test_update_parcel(client: AsyncClient, auth_headers):
    establishment = {"name": "Farm", "siret": "123456", "address": "Location", "surface_ha": 5}
    est_response = await client.post("/establishments", json=establishment, headers=auth_headers)
    est_id = est_response.json()["id"]
    tenant_headers = _tenant_headers(auth_headers, est_id)

    parcel = {
        "name": "Old Name",
        "establishment_id": est_id,
        "area_ha": 1.5,
        "crop_type": "ViÈ›Äƒ de vie",
        "coordinates": _coords(),
    }
    create_response = await client.post("/parcels", json=parcel, headers=tenant_headers)
    parcel_id = create_response.json()["id"]

    update_data = {
        "name": "New Name",
        "establishment_id": est_id,
        "area_ha": 2.0,
        "crop_type": "ViÈ›Äƒ de vie",
        "coordinates": _coords(),
    }
    response = await client.put(f"/parcels/{parcel_id}", json=update_data, headers=tenant_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_parcel(client: AsyncClient, auth_headers):
    establishment = {"name": "Farm", "siret": "123456", "address": "Location", "surface_ha": 5}
    est_response = await client.post("/establishments", json=establishment, headers=auth_headers)
    est_id = est_response.json()["id"]
    tenant_headers = _tenant_headers(auth_headers, est_id)

    parcel = {
        "name": "To Delete",
        "establishment_id": est_id,
        "area_ha": 1.5,
        "crop_type": "ViÈ›Äƒ de vie",
        "coordinates": _coords(),
    }
    create_response = await client.post("/parcels", json=parcel, headers=tenant_headers)
    parcel_id = create_response.json()["id"]

    response = await client.delete(f"/parcels/{parcel_id}", headers=tenant_headers)
    assert response.status_code == 204

    get_response = await client.get(f"/parcels/by-establishment/{est_id}", headers=tenant_headers)
    assert get_response.status_code == 200
    assert all(p["id"] != parcel_id for p in get_response.json())
