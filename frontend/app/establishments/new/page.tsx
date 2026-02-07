'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { establishmentsAPI } from '@/lib/api';
import { ErrorAlert } from '@/components/UIComponents';

export default function EstablishmentNewPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    siret: '',
    address: '',
    surface_ha: 0,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await establishmentsAPI.create(formData);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Eroare la creare fermă');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-green-800">Adaugă exploatație</h1>
          <Link href="/dashboard" className="text-green-600 hover:text-green-700">
            Retour au tableau de bord
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
          <h2 className="text-xl font-semibold mb-4">Detalii fermă</h2>
          <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nume</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SIRET</label>
              <input
                type="text"
                value={formData.siret}
                onChange={(e) => setFormData({ ...formData, siret: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Adresă</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Suprafață (ha)</label>
              <input
                type="number"
                step="0.01"
                value={formData.surface_ha}
                onChange={(e) => setFormData({ ...formData, surface_ha: parseFloat(e.target.value) || 0 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div className="md:col-span-2 flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg disabled:opacity-60"
              >
                {loading ? 'Se salvează...' : 'Salvează'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/dashboard')}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-6 py-2 rounded-lg"
              >
                Anulează
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
