from __future__ import annotations

import asyncio
import csv
import io
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import httpx

from app.ephy.client import EphyDatasetClient, DatasetInfo
from app.ephy.index import EphyIndex, EphyProduct, EphyUsage


@dataclass(frozen=True)
class SyncResult:
    updated: bool
    last_update: str
    products_count: int
    usages_count: int


class EphySyncService:
    def __init__(
        self,
        index: EphyIndex,
        dataset_api_url: str,
        storage_dir: Path,
        viticulture_only: bool = True,
    ) -> None:
        self._index = index
        self._client = EphyDatasetClient(dataset_api_url)
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._viticulture_only = viticulture_only
        self._lock = asyncio.Lock()

    async def ensure_fresh(self) -> SyncResult:
        async with self._lock:
            self._index.init_schema()
            info = self._client.get_dataset_info()
            last_update = info.last_update or ""
            current_update = self._index.get_meta("last_update")
            if current_update == last_update and current_update:
                return SyncResult(
                    updated=False,
                    last_update=current_update,
                    products_count=int(self._index.get_meta("products_count") or 0),
                    usages_count=int(self._index.get_meta("usages_count") or 0),
                )

            result = await asyncio.to_thread(self._sync, info)
            return result

    def _sync(self, info: DatasetInfo) -> SyncResult:
        self._index.init_schema()
        resource = self._client.pick_utf8_zip(info)
        if not resource:
            raise RuntimeError("No ZIP resource found for E-Phy dataset")

        zip_path = self._download_zip(resource.url)
        with zipfile.ZipFile(zip_path) as zf:
            produits_stream, usages_stream = self._open_csv_streams(zf)
            usages, vigne_amms = self._parse_usages(usages_stream)
            products = self._parse_products(produits_stream)

        self._index.reset()
        self._index.bulk_insert_usages(usages)
        self._index.bulk_insert_products(products, vigne_amms)

        self._index.set_meta("last_update", info.last_update or "")
        self._index.set_meta("dataset_id", info.dataset_id)
        self._index.set_meta("synced_at", datetime.now(timezone.utc).isoformat())
        self._index.set_meta("products_count", str(len(vigne_amms)))
        self._index.set_meta("usages_count", str(len(usages)))

        return SyncResult(
            updated=True,
            last_update=info.last_update or "",
            products_count=len(vigne_amms),
            usages_count=len(usages),
        )

    def _download_zip(self, url: str) -> Path:
        target = self._storage_dir / "ephy_latest.zip"
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            target.write_bytes(response.content)
        return target

    def _open_csv_streams(self, zf: zipfile.ZipFile) -> tuple[io.TextIOWrapper, io.TextIOWrapper]:
        produits_name = self._pick_file(zf, "produits_utf8.csv")
        usages_name = self._pick_file(zf, "usages_des_produits_autorises_utf8.csv")
        if not produits_name or not usages_name:
            raise RuntimeError("Missing required CSV files in E-Phy ZIP")

        produits_file = zf.open(produits_name)
        usages_file = zf.open(usages_name)
        return (
            io.TextIOWrapper(produits_file, encoding="utf-8", errors="replace"),
            io.TextIOWrapper(usages_file, encoding="utf-8", errors="replace"),
        )

    @staticmethod
    def _pick_file(zf: zipfile.ZipFile, suffix: str) -> Optional[str]:
        for name in zf.namelist():
            if name.lower().endswith(suffix):
                return name
        return None

    def _parse_products(self, stream: io.TextIOWrapper) -> list[EphyProduct]:
        reader = csv.DictReader(stream, delimiter=";")
        products: list[EphyProduct] = []
        for row in reader:
            products.append(
                EphyProduct(
                    amm=row.get("numero AMM", "").strip(),
                    name=row.get("nom produit", "").strip(),
                    titulaire=row.get("titulaire", "").strip(),
                    fonctions=row.get("fonctions", "").strip(),
                    etat=row.get("Etat d’autorisation", "").strip(),
                    type_produit=row.get("type produit", "").strip(),
                    type_commercial=row.get("type commercial", "").strip(),
                    gamme_usage=row.get("gamme usage", "").strip(),
                    mentions=row.get("mentions autorisees", "").strip(),
                    restrictions=row.get("restrictions usage", "").strip(),
                    substances=row.get("Substances actives", "").strip(),
                    formulations=row.get("formulations", "").strip(),
                    ref_amm=row.get("Numéro AMM du produit de référence", "").strip(),
                    ref_name=row.get("Nom du produit de référence", "").strip(),
                )
            )
        return products

    def _parse_usages(self, stream: io.TextIOWrapper) -> tuple[list[EphyUsage], set[str]]:
        reader = csv.DictReader(stream, delimiter=";")
        usages: list[EphyUsage] = []
        vigne_amms: set[str] = set()
        for row in reader:
            identifiant = row.get("identifiant usage", "").strip()
            if self._viticulture_only and "vigne" not in identifiant.lower():
                continue
            amm = row.get("numero AMM", "").strip()
            if amm:
                vigne_amms.add(amm)
            usages.append(
                EphyUsage(
                    amm=amm,
                    identifiant_usage=identifiant,
                    etat_usage=row.get("etat usage", "").strip(),
                    dose=row.get("dose retenue", "").strip(),
                    dose_unite=row.get("dose retenue unite", "").strip(),
                    dar_jour=row.get("delai avant recolte jour", "").strip(),
                    dar_bbch=row.get("delai avant recolte bbch", "").strip(),
                    max_apps=row.get("nombre max d'application", "").strip(),
                    intervalle_min=row.get("intervalle minimum entre applications (jour)", "").strip(),
                    date_decision=row.get(" date decision", "").strip(),
                    date_fin_distribution=row.get("date fin distribution", "").strip(),
                    date_fin_utilisation=row.get("date fin utilisation", "").strip(),
                    condition_emploi=row.get("condition emploi", "").strip(),
                    znt_aquatique=row.get("ZNT aquatique (en m)", "").strip(),
                    znt_arthropodes=row.get("ZNT arthropodes non cibles (en m)", "").strip(),
                    znt_plantes=row.get("ZNT plantes non cibles (en m)", "").strip(),
                    mentions=row.get("mentions autorisees", "").strip(),
                )
            )
        return usages, vigne_amms
