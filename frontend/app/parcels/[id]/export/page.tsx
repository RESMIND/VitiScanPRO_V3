'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { parcelsAPI } from '@/lib/api';
import { ErrorAlert } from '@/components/UIComponents';

export default function ParcelExportPage() {
  const params = useParams();
  const router = useRouter();
  const parcelId = params?.id as string;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleExport = async () => {
    setLoading(true);
    setError('');
    try {
      const blob = await parcelsAPI.exportDraaf(parcelId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `draaf_parcel_${parcelId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Eroare la export PDF DRAAF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-green-800">Export PDF DRAAF</h1>
          <Link href={`/parcels/${parcelId}`} className="text-green-600 hover:text-green-700">
            Retour à la parcelle
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6">
            <ErrorAlert message={error} onDismiss={() => setError('')} />
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl">
          <h2 className="text-xl font-semibold mb-2">Generează raport DRAAF</h2>
          <p className="text-gray-600 mb-6">
            Le PDF inclura les traitements pour cette parcelle.
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleExport}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg disabled:opacity-60"
            >
              {loading ? 'Se generează...' : 'Descarcă PDF'}
            </button>
            <button
              onClick={() => router.push(`/parcels/${parcelId}`)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-6 py-2 rounded-lg"
            >
              Anulează
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
