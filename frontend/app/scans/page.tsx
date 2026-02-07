'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { LoadingSpinner, EmptyState, ErrorAlert } from '@/components/UIComponents';
import { establishmentsAPI, parcelsAPI, scansAPI } from '@/lib/api';

interface Scan {
  id: string;
  parcel_id: string;
  parcel_name?: string;
  establishment_name?: string;
  image_url?: string;
  scan_date: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_result?: {
    disease_detected?: boolean;
    confidence?: number;
    recommendations?: string[];
  };
  created_at: string;
}

interface Establishment {
  id: string;
  name: string;
}

interface Parcel {
  id: string;
  name: string;
  establishment_id: string;
}

function ScansListPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const parcelFilter = searchParams?.get('parcel_id');

  const [scans, setScans] = useState<Scan[]>([]);
  const [establishments, setEstablishments] = useState<Establishment[]>([]);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<'date' | 'status'>('date');

  useEffect(() => {
    fetchScans();
  }, [parcelFilter]);

  const fetchScans = async () => {
    setLoading(true);
    setError('');

    try {
      const userEstablishments: Establishment[] = await establishmentsAPI.getMine();
      setEstablishments(userEstablishments || []);

      if (!userEstablishments || userEstablishments.length === 0) {
        setParcels([]);
        setScans([]);
        return;
      }

      const parcelsByEstablishment = await Promise.all(
        userEstablishments.map((est) => parcelsAPI.getByEstablishment(est.id))
      );
      const allParcels: Parcel[] = parcelsByEstablishment.flat().map((p: any) => ({
        id: p.id,
        name: p.name,
        establishment_id: p.establishment_id,
      }));
      setParcels(allParcels);

      if (parcelFilter) {
        const scansData = await scansAPI.getByParcel(parcelFilter);
        const parcel = allParcels.find((p) => p.id === parcelFilter);
        const establishment = userEstablishments.find((e) => e.id === parcel?.establishment_id);
        const mapped = (scansData || []).map((scan: any) => ({
          id: scan.scan_id ?? scan.id,
          parcel_id: parcelFilter,
          parcel_name: parcel?.name,
          establishment_name: establishment?.name,
          image_url: scan.image_url,
          scan_date: scan.uploaded_at ?? scan.scan_date ?? scan.created_at,
          created_at: scan.uploaded_at ?? scan.created_at ?? new Date().toISOString(),
          status: 'completed',
          analysis_result: scan.analysis_result,
        })) as Scan[];
        setScans(mapped);
        return;
      }

      const scansByParcel = await Promise.all(
        allParcels.map(async (parcel) => {
          try {
            const scansData = await scansAPI.getByParcel(parcel.id);
            const establishment = userEstablishments.find((e) => e.id === parcel.establishment_id);
            return (scansData || []).map((scan: any) => ({
              id: scan.scan_id ?? scan.id,
              parcel_id: parcel.id,
              parcel_name: parcel.name,
              establishment_name: establishment?.name,
              image_url: scan.image_url,
              scan_date: scan.uploaded_at ?? scan.scan_date ?? scan.created_at,
              created_at: scan.uploaded_at ?? scan.created_at ?? new Date().toISOString(),
              status: 'completed',
              analysis_result: scan.analysis_result,
            })) as Scan[];
          } catch {
            return [] as Scan[];
          }
        })
      );

      setScans(scansByParcel.flat());
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Eroare la încărcarea scanărilor';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (scanId: string) => {
    if (!confirm('Sigur vrei să ștergi această scanare?')) return;

    setError('Ștergerea scanărilor nu este disponibilă încă.');
  };

  const filteredScans = scans
    .filter(s => !statusFilter || s.status === statusFilter)
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.scan_date).getTime() - new Date(a.scan_date).getTime();
      }
      return a.status.localeCompare(b.status);
    });

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      processing: 'bg-blue-100 text-blue-800 border-blue-300',
      completed: 'bg-green-100 text-green-800 border-green-300',
      failed: 'bg-red-100 text-red-800 border-red-300'
    };

    const icons = {
      pending: '⏳',
      processing: '⚙️',
      completed: '✅',
      failed: '❌'
    };

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${styles[status as keyof typeof styles]}`}>
        <span className="mr-1">{icons[status as keyof typeof icons]}</span>
        {status.toUpperCase()}
      </span>
    );
  };

  const stats = {
    total: scans.length,
    pending: scans.filter(s => s.status === 'pending').length,
    processing: scans.filter(s => s.status === 'processing').length,
    completed: scans.filter(s => s.status === 'completed').length,
    failed: scans.filter(s => s.status === 'failed').length
  };

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
              <h1 className="text-3xl font-bold text-gray-900">📸 Scanări</h1>
              <p className="mt-1 text-sm text-gray-600">
                {filteredScans.length} {filteredScans.length === 1 ? 'scanare' : 'scanări'}
                {parcelFilter && ' pentru parcela selectată'}
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <Link
                href="/scans/new"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Scanare Nouă
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Pending</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Processing</div>
            <div className="text-2xl font-bold text-blue-600">{stats.processing}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Completed</div>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Failed</div>
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🔍 Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Toate</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ⬇️ Sortează
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="date">Data (mai recente)</option>
                <option value="status">Status</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

        {/* Scans Grid */}
        {filteredScans.length === 0 ? (
          <EmptyState
            icon="📸"
            title={parcels.length === 0 ? 'Nu există parcele' : 'Nicio scanare găsită'}
            description={
              parcels.length === 0
                ? 'Ajoutez une parcelle avant de télécharger des analyses'
                : 'Adaugă prima ta scanare pentru a începe monitorizarea culturilor'
            }
            action={
              parcels.length === 0
                ? { label: 'Ajouter une parcelle', onClick: () => router.push('/parcels/new') }
                : { label: 'Adaugă Scanare', onClick: () => router.push('/scans/new') }
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredScans.map((scan) => (
              <div key={scan.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
                {/* Image */}
                <div className="aspect-video bg-gray-200 relative">
                  {scan.image_url ? (
                    <img
                      src={scan.image_url}
                      alt="Scan"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-4xl">
                      📸
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    {getStatusBadge(scan.status)}
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {scan.parcel_name || 'Parcelle inconnue'}
                      </h3>
                      {scan.establishment_name && (
                        <p className="text-sm text-gray-600">{scan.establishment_name}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {new Date(scan.scan_date).toLocaleDateString('ro-RO', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>

                    {scan.analysis_result?.disease_detected !== undefined && (
                      <div className={`flex items-center text-sm ${scan.analysis_result.disease_detected ? 'text-red-600' : 'text-green-600'}`}>
                        {scan.analysis_result.disease_detected ? '⚠️ Boală detectată' : '✅ Fără probleme'}
                        {scan.analysis_result.confidence && (
                          <span className="ml-2 text-xs text-gray-500">
                            ({Math.round(scan.analysis_result.confidence * 100)}% confidence)
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <Link
                      href={`/parcels/${scan.parcel_id}`}
                      className="flex-1 text-center px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                    >
                      Voir la parcelle
                    </Link>
                    <button
                      onClick={() => handleDelete(scan.id)}
                      className="px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700"
                    >
                      Șterge
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ScansListPageWrapper() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ScansListPage />
    </Suspense>
  );
}
