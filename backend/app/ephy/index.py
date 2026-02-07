from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class EphyProduct:
    amm: str
    name: str
    titulaire: str
    fonctions: str
    etat: str
    type_produit: str
    type_commercial: str
    gamme_usage: str
    mentions: str
    restrictions: str
    substances: str
    formulations: str
    ref_amm: str
    ref_name: str


@dataclass(frozen=True)
class EphyUsage:
    amm: str
    identifiant_usage: str
    etat_usage: str
    dose: str
    dose_unite: str
    dar_jour: str
    dar_bbch: str
    max_apps: str
    intervalle_min: str
    date_decision: str
    date_fin_distribution: str
    date_fin_utilisation: str
    condition_emploi: str
    znt_aquatique: str
    znt_arthropodes: str
    znt_plantes: str
    mentions: str


class EphyIndex:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode = WAL;
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    amm TEXT PRIMARY KEY,
                    name TEXT,
                    titulaire TEXT,
                    fonctions TEXT,
                    etat TEXT,
                    type_produit TEXT,
                    type_commercial TEXT,
                    gamme_usage TEXT,
                    mentions TEXT,
                    restrictions TEXT,
                    substances TEXT,
                    formulations TEXT,
                    ref_amm TEXT,
                    ref_name TEXT,
                    has_vigne_usage INTEGER DEFAULT 0
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS products_fts
                USING fts5(amm, name, titulaire, fonctions);

                CREATE TABLE IF NOT EXISTS usages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amm TEXT NOT NULL,
                    identifiant_usage TEXT,
                    etat_usage TEXT,
                    dose TEXT,
                    dose_unite TEXT,
                    dar_jour TEXT,
                    dar_bbch TEXT,
                    max_apps TEXT,
                    intervalle_min TEXT,
                    date_decision TEXT,
                    date_fin_distribution TEXT,
                    date_fin_utilisation TEXT,
                    condition_emploi TEXT,
                    znt_aquatique TEXT,
                    znt_arthropodes TEXT,
                    znt_plantes TEXT,
                    mentions TEXT
                );

                CREATE INDEX IF NOT EXISTS usages_amm_idx ON usages(amm);
                CREATE INDEX IF NOT EXISTS products_etat_idx ON products(etat);
                """
            )

    def reset(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                DELETE FROM products;
                DELETE FROM products_fts;
                DELETE FROM usages;
                """
            )

    def set_meta(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_meta(self, key: str) -> Optional[str]:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def bulk_insert_products(self, products: Iterable[EphyProduct], has_vigne: set[str]) -> None:
        with self.connect() as conn:
            product_rows = []
            fts_rows = []
            for product in products:
                if product.amm not in has_vigne:
                    continue
                product_rows.append(
                    (
                        product.amm,
                        product.name,
                        product.titulaire,
                        product.fonctions,
                        product.etat,
                        product.type_produit,
                        product.type_commercial,
                        product.gamme_usage,
                        product.mentions,
                        product.restrictions,
                        product.substances,
                        product.formulations,
                        product.ref_amm,
                        product.ref_name,
                        1,
                    )
                )
                fts_rows.append((product.amm, product.name, product.titulaire, product.fonctions))
            conn.executemany(
                """
                INSERT OR REPLACE INTO products(
                    amm, name, titulaire, fonctions, etat, type_produit, type_commercial,
                    gamme_usage, mentions, restrictions, substances, formulations,
                    ref_amm, ref_name, has_vigne_usage
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                product_rows,
            )
            conn.executemany(
                "INSERT INTO products_fts(amm, name, titulaire, fonctions) VALUES(?, ?, ?, ?)",
                fts_rows,
            )

    def bulk_insert_usages(self, usages: Iterable[EphyUsage]) -> None:
        with self.connect() as conn:
            rows = [
                (
                    usage.amm,
                    usage.identifiant_usage,
                    usage.etat_usage,
                    usage.dose,
                    usage.dose_unite,
                    usage.dar_jour,
                    usage.dar_bbch,
                    usage.max_apps,
                    usage.intervalle_min,
                    usage.date_decision,
                    usage.date_fin_distribution,
                    usage.date_fin_utilisation,
                    usage.condition_emploi,
                    usage.znt_aquatique,
                    usage.znt_arthropodes,
                    usage.znt_plantes,
                    usage.mentions,
                )
                for usage in usages
            ]
            conn.executemany(
                """
                INSERT INTO usages(
                    amm, identifiant_usage, etat_usage, dose, dose_unite,
                    dar_jour, dar_bbch, max_apps, intervalle_min,
                    date_decision, date_fin_distribution, date_fin_utilisation,
                    condition_emploi, znt_aquatique, znt_arthropodes, znt_plantes, mentions
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def search_products(self, query: str, limit: int = 20, etat: Optional[str] = None) -> list[sqlite3.Row]:
        with self.connect() as conn:
            params = {"limit": limit}
            if query.isdigit():
                sql = "SELECT * FROM products WHERE amm LIKE :q"
                params["q"] = f"%{query}%"
                if etat and etat != "ALL":
                    sql += " AND etat = :etat"
                    params["etat"] = etat
                sql += " ORDER BY amm LIMIT :limit"
                return conn.execute(sql, params).fetchall()

            sanitized = self._fts_query(query)
            sql = """
                SELECT p.*
                FROM products_fts f
                JOIN products p ON p.amm = f.amm
                WHERE products_fts MATCH :q
            """
            params["q"] = sanitized
            if etat and etat != "ALL":
                sql += " AND p.etat = :etat"
                params["etat"] = etat
            sql += " LIMIT :limit"
            return conn.execute(sql, params).fetchall()

    def get_product(self, amm: str) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM products WHERE amm = ?", (amm,)).fetchone()

    def get_usages(self, amm: str, limit: int = 200) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM usages WHERE amm = ? LIMIT ?", (amm, limit)
            ).fetchall()

    @staticmethod
    def _fts_query(raw: str) -> str:
        tokens = []
        for chunk in raw.replace('"', " ").split():
            cleaned = "".join(ch for ch in chunk if ch.isalnum())
            if cleaned:
                tokens.append(f"{cleaned}*")
        return " AND ".join(tokens) if tokens else raw
