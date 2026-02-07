'use client';

import { useEffect, useMemo, useState } from 'react';
import { ephyAPI, EphyProductDetail, EphyProductSummary } from '@/lib/ephy';

interface EphyProductSearchProps {
  onSelect?: (product: EphyProductDetail) => void;
}

export default function EphyProductSearch({ onSelect }: EphyProductSearchProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<EphyProductSummary[]>([]);
  const [selected, setSelected] = useState<EphyProductDetail | null>(null);
  const [error, setError] = useState('');

  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setResults([]);
      return;
    }
    let isMounted = true;
    setLoading(true);
    setError('');
    ephyAPI
      .search(debouncedQuery)
      .then((data) => {
        if (!isMounted) return;
        setResults(data.results || []);
      })
      .catch((err) => {
        if (!isMounted) return;
        const message = err?.response?.data?.detail || err?.message || 'Recherche indisponible';
        setError(message);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [debouncedQuery]);

  const handleSelect = async (product: EphyProductSummary) => {
    setLoading(true);
    setError('');
    try {
      const detail = await ephyAPI.getProduct(product.numero_amm);
      setSelected(detail);
      onSelect?.(detail);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Détails indisponibles';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Rechercher un produit (AMM ou nom)"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-200"
        />
        {loading && <span className="text-xs text-gray-500">Chargement...</span>}
      </div>

      {error && <div className="mt-2 text-xs text-red-600">{error}</div>}

      <div className="mt-3 space-y-2">
        {results.map((product) => (
          <button
            key={product.numero_amm}
            onClick={() => handleSelect(product)}
            className="flex w-full items-start justify-between rounded-md border border-gray-100 px-3 py-2 text-left text-sm hover:border-green-400 hover:bg-green-50"
          >
            <div>
              <div className="font-semibold text-gray-900">{product.nom_produit}</div>
              <div className="text-xs text-gray-500">
                AMM {product.numero_amm} · {product.titulaire}
              </div>
            </div>
            <span className="rounded-full bg-green-100 px-2 py-1 text-[10px] font-semibold text-green-700">
              {product.etat_produit || 'AUTORISE'}
            </span>
          </button>
        ))}
      </div>

      {selected && (
        <div className="mt-4 rounded-md border border-green-200 bg-green-50 p-3 text-sm">
          <div className="flex items-center justify-between">
            <div className="font-semibold text-gray-900">{selected.product.nom_produit}</div>
            <span className="text-xs text-gray-500">AMM {selected.product.numero_amm}</span>
          </div>
          <div className="mt-1 text-xs text-gray-600">{selected.product.fonctions}</div>

          <div className="mt-3 grid gap-2 text-xs text-gray-700">
            <div>
              <span className="font-semibold">Substances:</span> {selected.product.substances_actives}
            </div>
            <div>
              <span className="font-semibold">Formulation:</span> {selected.product.formulations}
            </div>
            <div>
              <span className="font-semibold">Usages viticoles:</span> {selected.usages.length}
            </div>
          </div>

          {onSelect && (
            <button
              onClick={() => onSelect(selected)}
              className="mt-3 rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700"
            >
              Utiliser pour traitement
            </button>
          )}
        </div>
      )}

      <div className="mt-4 text-[11px] text-gray-400">
        Données E-Phy — Anses, mise à jour hebdomadaire (Licence Ouverte).
      </div>
    </div>
  );
}

function useDebounce<T>(value: T, delay: number) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
