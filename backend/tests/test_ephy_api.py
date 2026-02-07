import asyncio
from pathlib import Path

import pytest

import app.routes.ephy as ephy_routes
from app.ephy.index import EphyIndex, EphyProduct, EphyUsage


@pytest.mark.asyncio
async def test_ephy_search_endpoint(client, tmp_path: Path):
    index = EphyIndex(tmp_path / "ephy.sqlite")
    index.init_schema()
    index.bulk_insert_usages(
        [
            EphyUsage(
                amm="123456",
                identifiant_usage="Vigne*Trt Part.Aer.*Mildiou(s)",
                etat_usage="AUTORISE",
                dose="2.5",
                dose_unite="kg/ha",
                dar_jour="21",
                dar_bbch="",
                max_apps="3",
                intervalle_min="",
                date_decision="2025-01-01",
                date_fin_distribution="",
                date_fin_utilisation="",
                condition_emploi="",
                znt_aquatique="20",
                znt_arthropodes="5",
                znt_plantes="",
                mentions="",
            )
        ]
    )
    index.bulk_insert_products(
        [
            EphyProduct(
                amm="123456",
                name="Produit Vigne",
                titulaire="Titulaire A",
                fonctions="Fongicide",
                etat="AUTORISE",
                type_produit="PPP",
                type_commercial="Type X",
                gamme_usage="Usage X",
                mentions="",
                restrictions="",
                substances="Substance A",
                formulations="WP",
                ref_amm="",
                ref_name="",
            )
        ],
        {"123456"},
    )

    async def _ensure_fresh():
        return None

    ephy_routes.index = index
    ephy_routes.sync_service.ensure_fresh = _ensure_fresh  # type: ignore[assignment]

    response = await client.get("/api/ephy/products/search", params={"q": "Produit"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["numero_amm"] == "123456"

    response = await client.get("/api/ephy/products/123456")
    assert response.status_code == 200
    payload = response.json()
    assert payload["product"]["numero_amm"] == "123456"
    assert len(payload["usages"]) == 1
