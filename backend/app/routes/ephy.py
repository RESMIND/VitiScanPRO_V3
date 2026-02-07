from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import EPHY_DATASET_API_URL, EPHY_STORAGE_PATH, EPHY_VITICULTURE_ONLY
from app.ephy.index import EphyIndex
from app.ephy.sync import EphySyncService
from app.routes.auth import get_current_admin_user

router = APIRouter(prefix="/api/ephy", tags=["E-Phy"])

index = EphyIndex(Path(EPHY_STORAGE_PATH))
sync_service = EphySyncService(
    index=index,
    dataset_api_url=EPHY_DATASET_API_URL,
    storage_dir=Path(EPHY_STORAGE_PATH).parent,
    viticulture_only=EPHY_VITICULTURE_ONLY,
)


@router.get("/status")
async def status():
    last_update = index.get_meta("last_update") or ""
    return {
        "last_update": last_update,
        "products_count": int(index.get_meta("products_count") or 0),
        "usages_count": int(index.get_meta("usages_count") or 0),
        "viticulture_only": EPHY_VITICULTURE_ONLY,
        "attribution": "Données E-Phy — Anses (Licence Ouverte)",
    }


@router.post("/sync")
async def sync(admin_user: dict = Depends(get_current_admin_user)):
    result = await sync_service.ensure_fresh()
    return {
        "updated": result.updated,
        "last_update": result.last_update,
        "products_count": result.products_count,
        "usages_count": result.usages_count,
    }


@router.get("/products/search")
async def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    etat: str = Query("AUTORISE"),
):
    await sync_service.ensure_fresh()
    rows = index.search_products(q, limit=limit, etat=etat)
    results = [
        {
            "numero_amm": row["amm"],
            "nom_produit": row["name"],
            "titulaire": row["titulaire"],
            "fonctions": row["fonctions"],
            "etat_produit": row["etat"],
            "type_produit": row["type_produit"],
            "type_commercial": row["type_commercial"],
            "gamme_usage": row["gamme_usage"],
            "mentions_autorisees": row["mentions"],
            "substances_actives": row["substances"],
        }
        for row in rows
    ]
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


@router.get("/products/{amm}")
async def get_product(amm: str, usage_limit: int = Query(200, ge=1, le=1000)):
    await sync_service.ensure_fresh()
    product = index.get_product(amm)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    usages = index.get_usages(amm, limit=usage_limit)
    return {
        "product": {
            "numero_amm": product["amm"],
            "nom_produit": product["name"],
            "titulaire": product["titulaire"],
            "fonctions": product["fonctions"],
            "etat_produit": product["etat"],
            "type_produit": product["type_produit"],
            "type_commercial": product["type_commercial"],
            "gamme_usage": product["gamme_usage"],
            "mentions_autorisees": product["mentions"],
            "substances_actives": product["substances"],
            "formulations": product["formulations"],
            "reference_amm": product["ref_amm"],
            "reference_nom": product["ref_name"],
        },
        "usages": [
            {
                "identifiant_usage": row["identifiant_usage"],
                "etat_usage": row["etat_usage"],
                "dose": row["dose"],
                "dose_unite": row["dose_unite"],
                "delai_avant_recolte_jour": row["dar_jour"],
                "delai_avant_recolte_bbch": row["dar_bbch"],
                "nombre_max_applications": row["max_apps"],
                "intervalle_min_jour": row["intervalle_min"],
                "date_decision": row["date_decision"],
                "date_fin_distribution": row["date_fin_distribution"],
                "date_fin_utilisation": row["date_fin_utilisation"],
                "condition_emploi": row["condition_emploi"],
                "znt_aquatique": row["znt_aquatique"],
                "znt_arthropodes": row["znt_arthropodes"],
                "znt_plantes": row["znt_plantes"],
                "mentions_autorisees": row["mentions"],
            }
            for row in usages
        ],
    }
