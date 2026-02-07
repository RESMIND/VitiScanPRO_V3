'use client';

import { useState } from 'react';
import EphyProductSearch from '@/components/EphyProductSearch';
import EphySearchBar from '@/components/EphySearchBar';
import { EphyProductDetail, EphyProductSummary } from '@/lib/ephy';

export default function EphyPage() {
  const [selected, setSelected] = useState<EphyProductDetail | null>(null);
  const [quickSelection, setQuickSelection] = useState<EphyProductSummary | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Recherche Produits Phyto (E-Phy)</h1>
          <p className="text-sm text-gray-600">
            Base officielle Anses. Filtrage viticole uniquement.
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700">Recherche rapide (header)</h2>
          <div className="mt-2">
            <EphySearchBar onSelect={setQuickSelection} />
          </div>
          {quickSelection && (
            <div className="mt-3 text-xs text-gray-600">
              Sélection rapide: {quickSelection.nom_produit} (AMM {quickSelection.numero_amm})
            </div>
          )}
        </div>

        <EphyProductSearch onSelect={setSelected} />

        {selected && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">Fiche produit</h2>
            <div className="mt-2 text-sm text-gray-700">
              <div className="font-semibold">{selected.product.nom_produit}</div>
              <div className="text-xs text-gray-500">AMM {selected.product.numero_amm}</div>
              <div className="mt-2 text-xs text-gray-600">
                Usages viticoles: {selected.usages.length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
