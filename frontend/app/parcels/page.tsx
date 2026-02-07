'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LoadingSpinner, EmptyState, ErrorAlert } from '@/components/UIComponents';
import { establishmentsAPI, parcelsAPI } from '@/lib/api';

interface Parcel {
  id: string;
  name: string;
  establishment_id: string;
  establishment_name?: string;
  surface_ha: number;
  crop_type?: string;
  coordinates: any;
  scan_count?: number;
  last_scan_date?: string;
  created_at: string;
}

interface Establishment {
  id: string;
  name: string;
}

export default function ParcelsListPage() {
  const router = useRouter();
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [establishments, setEstablishments] = useState<Establishment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [establishmentFilter, setEstablishmentFilter] = useState('');
  const [cropTypeFilter, setCropTypeFilter] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'surface' | 'scans' | 'date'>('name');

  useEffect(() => {
    fetchParcels();
  }, []);

  const fetchParcels = async () => {
    setLoading(true);
    setError('');
    
    try {
      const userEstablishments: Establishment[] = await establishmentsAPI.getMine();
      setEstablishments(userEstablishments || []);

      if (!userEstablishments || userEstablishments.length === 0) {
        setParcels([]);
        return;
      }

      const parcelsByEstablishment = await Promise.all(
        userEstablishments.map((est) => parcelsAPI.getByEstablishment(est.id))
      );

      const mergedParcels = parcelsByEstablishment.flat().map((parcel: any) => {
        const est = userEstablishments.find((e) => e.id === parcel.establishment_id);
        return {
          ...parcel,
          surface_ha: parcel.area_ha ?? parcel.surface_ha,
          establishment_name: est?.name || parcel.establishment_name,
        } as Parcel;
      });

      setParcels(mergedParcels);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Eroare la încărcarea parcelelor';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (parcelId: string) => {
    if (!confirm('Vous êtes sûr de vouloir supprimer cette parcelle ?')) return;

    try {
      await parcelsAPI.delete(parcelId);
      setParcels(parcels.filter(p => p.id !== parcelId));
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Eroare la ștergerea parcelei';
      setError(message);
    }
  };

  // Filter & Sort Logic
  const filteredParcels = parcels
    .filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.establishment_name?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesEstablishment = !establishmentFilter || p.establishment_id === establishmentFilter;
      const matchesCropType = !cropTypeFilter || p.crop_type === cropTypeFilter;
      
      return matchesSearch && matchesEstablishment && matchesCropType;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'surface':
          return b.surface_ha - a.surface_ha;
        case 'scans':
          return (b.scan_count || 0) - (a.scan_count || 0);
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        default:
          return a.name.localeCompare(b.name);
      }
    });

  // Get unique values for filters
  const establishmentOptions = Array.from(new Set(
    parcels.map(p => ({ id: p.establishment_id, name: p.establishment_name }))
  ));
  const cropTypes = Array.from(new Set(parcels.map(p => p.crop_type).filter(Boolean)));

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">🌱 Parcelele Mele</h1>
              <p className="mt-1 text-sm text-gray-600">
                {filteredParcels.length} {filteredParcels.length === 1 ? 'parcelle' : 'parcelles'}
                {searchQuery && ` - filtrate după "${searchQuery}"`}
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <Link
                href="/parcels/new"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Ajouter une parcelle
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🔍 Caută
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Nom de la parcelle ou établissement..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            {/* Establishment Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🏛️ Exploatație
              </label>
              <select
                value={establishmentFilter}
                onChange={(e) => setEstablishmentFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Toate</option>
                {establishmentOptions.map((est) => (
                  <option key={est.id} value={est.id}>
                    {est.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Crop Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🍇 Soi
              </label>
              <select
                value={cropTypeFilter}
                onChange={(e) => setCropTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Toate</option>
                {cropTypes.map((crop) => (
                  <option key={crop} value={crop}>
                    {crop}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ⬇️ Sortează
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="name">Nume</option>
                <option value="surface">Suprafață</option>
                <option value="scans">Scanări</option>
                <option value="date">Data creării</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

        {/* Parcels Table */}
        {filteredParcels.length === 0 ? (
          <EmptyState
            icon="🌱"
            title={establishments.length === 0 ? "Aucun établissement trouvé" : "Aucune parcelle trouvée"}
            description={
              establishments.length === 0
                ? "Creează mai întâi o exploatație în Dashboard"
                : (searchQuery ? "Essayez de modifier les filtres" : "Ajoutez votre première parcelle pour commencer")
            }
            action={
              establishments.length === 0
                ? { label: 'Aller au Tableau de bord', onClick: () => router.push('/dashboard') }
                : (!searchQuery ? { label: 'Ajouter une parcelle', onClick: () => router.push('/parcels/new') } : undefined)
            }
          />
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nom de la parcelle
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Exploatație
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Suprafață
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Soi
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Scanări
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acțiuni
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredParcels.map((parcel) => (
                    <tr key={parcel.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                            <span className="text-green-600 font-semibold">🌱</span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{parcel.name}</div>
                            {parcel.last_scan_date && (
                              <div className="text-xs text-gray-500">
                                Ultimă scanare: {new Date(parcel.last_scan_date).toLocaleDateString('ro-RO')}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {parcel.establishment_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{parcel.surface_ha} ha</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                          {parcel.crop_type || 'Necunoscut'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {parcel.scan_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <Link
                            href={`/parcels/${parcel.id}`}
                            className="text-green-600 hover:text-green-900"
                          >
                            Vezi
                          </Link>
                          <button
                            onClick={() => handleDelete(parcel.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Șterge
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards */}
            <div className="md:hidden divide-y divide-gray-200">
              {filteredParcels.map((parcel) => (
                <div key={parcel.id} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{parcel.name}</h3>
                      <p className="text-sm text-gray-600">{parcel.establishment_name}</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                      {parcel.crop_type || 'Necunoscut'}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <div className="text-xs text-gray-500">Suprafață</div>
                      <div className="text-sm font-medium text-gray-900">{parcel.surface_ha} ha</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Scanări</div>
                      <div className="text-sm font-medium text-gray-900">{parcel.scan_count || 0}</div>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Link
                      href={`/parcels/${parcel.id}`}
                      className="flex-1 text-center px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
                    >
                      Vezi Detalii
                    </Link>
                    <button
                      onClick={() => handleDelete(parcel.id)}
                      className="px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700"
                    >
                      Șterge
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
