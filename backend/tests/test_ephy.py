import csv
import io
import zipfile
from pathlib import Path

import pytest

from app.ephy.client import DatasetInfo, DatasetResource
from app.ephy.index import EphyIndex
from app.ephy.sync import EphySyncService


def _build_zip(path: Path) -> None:
    produits_header = [
        "type produit",
        "numero AMM",
        "nom produit",
        "seconds noms commerciaux",
        "titulaire",
        "type commercial",
        "gamme usage",
        "mentions autorisees",
        "restrictions usage",
        "restrictions usage libelle",
        "Substances actives",
        "fonctions",
        "formulations",
        "Etat d’autorisation",
        "Date de retrait du produit",
        "Date de première autorisation",
        "Numéro AMM du produit de référence",
        "Nom du produit de référence",
    ]
    produits_rows = [
        [
            "PPP",
            "123456",
            "Produit Vigne",
            "",
            "Titulaire A",
            "Type X",
            "Usage X",
            "Mentions",
            "",
            "",
            "Substance A",
            "Fongicide",
            "WP",
            "AUTORISE",
            "",
            "",
            "",
            "",
        ],
        [
            "PPP",
            "999999",
            "Produit Cereales",
            "",
            "Titulaire B",
            "Type Y",
            "Usage Y",
            "Mentions",
            "",
            "",
            "Substance B",
            "Herbicide",
            "SC",
            "AUTORISE",
            "",
            "",
            "",
            "",
        ],
    ]

    usages_header = [
        "type produit",
        "numero AMM",
        "nom produit",
        "seconds noms commerciaux",
        "titulaire",
        "type commercial",
        "gamme usage",
        "mentions autorisees",
        "Substances actives",
        "fonctions",
        "formulations",
        "identifiant usage lib court",
        "identifiant usage",
        " date decision",
        "stade cultural min (BBCH)",
        "stade cultural max (BBCH)",
        "etat usage",
        "dose retenue",
        "dose retenue unite",
        "delai avant recolte jour",
        "delai avant recolte bbch",
        "nombre max d'application",
        "date fin distribution",
        "date fin utilisation",
        "condition emploi",
        "ZNT aquatique (en m)",
        "ZNT arthropodes non cibles (en m)",
        "ZNT plantes non cibles (en m)",
        "mentions autorisees",
    ]
    usages_rows = [
        [
            "PPP",
            "123456",
            "Produit Vigne",
            "",
            "Titulaire A",
            "Type X",
            "Usage X",
            "Mentions",
            "Substance A",
            "Fongicide",
            "WP",
            "",
            "Vigne*Trt Part.Aer.*Mildiou(s)",
            "2025-01-01",
            "",
            "",
            "AUTORISE",
            "2.5",
            "kg/ha",
            "21",
            "",
            "3",
            "",
            "",
            "",
            "20",
            "5",
            "",
            "",
        ],
        [
            "PPP",
            "999999",
            "Produit Cereales",
            "",
            "Titulaire B",
            "Type Y",
            "Usage Y",
            "Mentions",
            "Substance B",
            "Herbicide",
            "SC",
            "",
            "Cereales*Trt Part.Aer.*Adventices",
            "2025-01-01",
            "",
            "",
            "AUTORISE",
            "1.0",
            "l/ha",
            "0",
            "",
            "1",
            "",
            "",
            "",
            "10",
            "5",
            "",
            "",
        ],
    ]

    with zipfile.ZipFile(path, "w") as zf:
        produits_buf = io.StringIO()
        writer = csv.writer(produits_buf, delimiter=";")
        writer.writerow(produits_header)
        writer.writerows(produits_rows)
        zf.writestr("produits_utf8.csv", produits_buf.getvalue())

        usages_buf = io.StringIO()
        writer = csv.writer(usages_buf, delimiter=";")
        writer.writerow(usages_header)
        writer.writerows(usages_rows)
        zf.writestr("usages_des_produits_autorises_utf8.csv", usages_buf.getvalue())


@pytest.mark.asyncio
async def test_ephy_sync_and_search(tmp_path: Path):
    zip_path = tmp_path / "ephy.zip"
    _build_zip(zip_path)

    index = EphyIndex(tmp_path / "ephy.sqlite")
    service = EphySyncService(
        index=index,
        dataset_api_url="https://example.com/dataset",
        storage_dir=tmp_path,
        viticulture_only=True,
    )

    info = DatasetInfo(
        dataset_id="dataset",
        last_update="2026-02-03T00:00:00Z",
        resources=[DatasetResource(resource_id="zip", title="utf8.zip", url="file", format="zip")],
    )

    def _download_zip(_url: str) -> Path:
        return zip_path

    service._download_zip = _download_zip  # type: ignore[assignment]

    result = service._sync(info)
    assert result.updated is True
    assert result.products_count == 1
    assert result.usages_count == 1

    rows = index.search_products("Produit", limit=10, etat="AUTORISE")
    assert len(rows) == 1
    assert rows[0]["amm"] == "123456"

    product = index.get_product("123456")
    assert product is not None
    usages = index.get_usages("123456")
    assert len(usages) == 1
    assert "Vigne" in usages[0]["identifiant_usage"]
