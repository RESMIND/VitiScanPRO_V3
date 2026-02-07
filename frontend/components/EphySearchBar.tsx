'use client';

import { useEffect, useState } from 'react';
import { ephyAPI, EphyProductSummary } from '@/lib/ephy';

interface EphySearchBarProps {
  onSelect?: (product: EphyProductSummary) => void;
}

export default function EphySearchBar({ onSelect }: EphySearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EphyProductSummary[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      const data = await ephyAPI.search(query, 8);
      setResults(data.results || []);
      setOpen(true);
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="relative">
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Recherche e-Phy (AMM ou nom)"
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-200"
      />
      {open && results.length > 0 && (
        <div className="absolute z-10 mt-2 w-full rounded-md border border-gray-200 bg-white shadow-lg">
          {results.map((item) => (
            <button
              key={item.numero_amm}
              onClick={() => {
                onSelect?.(item);
                setOpen(false);
              }}
              className="flex w-full flex-col px-3 py-2 text-left text-sm hover:bg-green-50"
            >
              <span className="font-semibold text-gray-900">{item.nom_produit}</span>
              <span className="text-xs text-gray-500">AMM {item.numero_amm}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
