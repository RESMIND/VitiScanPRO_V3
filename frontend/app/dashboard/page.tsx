'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI, establishmentsAPI, parcelsAPI, scansAPI } from '@/lib/api';
import { EmptyState, ErrorAlert } from '@/components/UIComponents';

interface User {
  email?: string;
  full_name?: string;
  username?: string;
  role: string;
}

interface Establishment {
  id: string;
  name: string;
  siret: string;
  address: string;
  surface_ha: number;
  created_at: string;
}

interface Parcel {
  id: string;
  name: string;
  establishment_name?: string;
  crop_type?: string;
  surface_ha: number;
}

interface Scan {
  id: string;
  parcel_id: string;
  parcel_name?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  scan_date: string;
  image_url?: string;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [establishments, setEstablishments] = useState<Establishment[]>([]);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const [stats, setStats] = useState({
    totalParcels: 0,
    totalSurface: 0,
    totalScans: 0,
    recentScansCount: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    siret: '',
    address: '',
    surface_ha: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      // Load user and establishments
      const [userProfile, userEstablishments] = await Promise.all([
        authAPI.getProfile(),
        establishmentsAPI.getMine(),
      ]);

      const displayName =
        userProfile.full_name ||
        userEstablishments?.[0]?.name ||
        'Utilizator';

      setUser({
        ...userProfile,
        full_name: displayName
      });
      setEstablishments(userEstablishments || []);

      if (!userEstablishments || userEstablishments.length === 0) {
        setParcels([]);
        setRecentScans([]);
        setStats({ totalParcels: 0, totalSurface: 0, totalScans: 0, recentScansCount: 0 });
        return;
      }

      const parcelsByEstablishment = await Promise.all(
        userEstablishments.map((est: Establishment) => parcelsAPI.getByEstablishment(est.id))
      );

      const parcelsData = parcelsByEstablishment.flat().map((parcel: any) => {
        const est = userEstablishments.find((e: Establishment) => e.id === parcel.establishment_id);
        return {
          ...parcel,
          surface_ha: parcel.area_ha ?? parcel.surface_ha,
          establishment_name: est?.name || parcel.establishment_name
        } as Parcel;
      });
      setParcels(parcelsData);

      const scansByParcel = await Promise.all(
        parcelsData.map(async (parcel) => {
          try {
            const scans = await scansAPI.getByParcel(parcel.id);
            return scans.map((scan: any) => ({
              id: scan.scan_id ?? scan.id,
              parcel_id: parcel.id,
              parcel_name: parcel.name,
              status: 'completed',
              scan_date: scan.uploaded_at ?? scan.scan_date ?? scan.created_at,
              created_at: scan.uploaded_at ?? scan.created_at ?? new Date().toISOString(),
              image_url: scan.image_url
            })) as Scan[];
          } catch {
            return [] as Scan[];
          }
        })
      );

      const scansData = scansByParcel.flat();

      // Calculate stats
      const totalSurface = parcelsData.reduce((sum: number, p: Parcel) => sum + p.surface_ha, 0);
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const recentScansCount = scansData.filter((s: Scan) => 
        new Date(s.created_at) >= sevenDaysAgo
      ).length;

      setStats({
        totalParcels: parcelsData.length,
        totalSurface: Math.round(totalSurface * 100) / 100,
        totalScans: scansData.length,
        recentScansCount
      });

      // Get last 5 scans
      const sortedScans = scansData.sort((a: Scan, b: Scan) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setRecentScans(sortedScans.slice(0, 5));

    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Eroare la încărcarea datelor';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const handleCreateEstablishment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await establishmentsAPI.create(formData);
      setShowCreateForm(false);
      setFormData({ name: '', siret: '', address: '', surface_ha: 0 });
      loadData(); // Reload establishments
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Eroare la creare fermă');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          <div className="text-xl text-gray-600">Chargement...</div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'pending': return '⏰';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-green-800">VitiScan v3</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-900 font-medium">Bun venit, {user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Deconectare
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6">
            <ErrorAlert message={error} onDismiss={() => setError('')} />
          </div>
        )}

        {establishments.length === 0 && !loading && (
          <div className="mb-8">
            <EmptyState
              icon="🏛️"
              title="Nu ai nicio exploatație"
              description="Adaugă prima exploatație pentru a începe"
              action={{ label: 'Adaugă exploatație', onClick: () => setShowCreateForm(true) }}
            />
          </div>
        )}
        {/* KPIs Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Parcels */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Parcele Totale</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalParcels}</p>
              </div>
              <div className="text-4xl">🌱</div>
            </div>
            <Link href="/parcels" className="text-green-600 hover:text-green-700 text-sm mt-4 inline-block">
              Vezi toate →
            </Link>
          </div>

          {/* Total Surface */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Suprafață Totală</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalSurface}</p>
                <p className="text-gray-500 text-xs">hectare</p>
              </div>
              <div className="text-4xl">📏</div>
            </div>
          </div>

          {/* Total Scans */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Scanări Totale</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.totalScans}</p>
              </div>
              <div className="text-4xl">📸</div>
            </div>
            <Link href="/scans" className="text-green-600 hover:text-green-700 text-sm mt-4 inline-block">
              Vezi toate →
            </Link>
          </div>

          {/* Recent Scans (Last 7 days) */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Scanări Recent</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.recentScansCount}</p>
                <p className="text-gray-500 text-xs">ultimele 7 zile</p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
        </div>

        {/* Recent Scans List */}
        {recentScans.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">Ultimele 5 scanări</h2>
              <Link href="/scans" className="text-green-600 hover:text-green-700 text-sm font-medium">
                Vezi toate →
              </Link>
            </div>
            <div className="space-y-3">
              {recentScans.map((scan) => (
                <Link
                  key={scan.id}
                  href={`/parcels/${scan.parcel_id}`}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    {scan.image_url && (
                      <img 
                        src={scan.image_url} 
                        alt="Scan preview"
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {scan.parcel_name || `Parcel ${scan.parcel_id.substring(0, 8)}`}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(scan.scan_date).toLocaleDateString('ro-RO')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(scan.status)}`}>
                      <span className="mr-1">{getStatusIcon(scan.status)}</span>
                      {scan.status}
                    </span>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Establishments Section */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Fermele mele</h2>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              + Adaugă fermă
            </button>
          </div>

          {/* Create Form */}
          {showCreateForm && (
            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h3 className="text-xl font-semibold mb-4">Fermă nouă</h3>
              <form onSubmit={handleCreateEstablishment} className="grid md:grid-cols-2 gap-4">
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
                    onChange={(e) => setFormData({ ...formData, surface_ha: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    required
                  />
                </div>
                <div className="md:col-span-2 flex gap-2">
                  <button
                    type="submit"
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
                  >
                    Salvează
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-6 py-2 rounded-lg"
                  >
                    Anulează
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Establishments List */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {establishments.length === 0 ? (
              <div className="col-span-full text-center py-12 bg-white rounded-lg shadow-md">
                <p className="text-gray-500 text-lg">Nu există ferme încă. Creează prima fermă!</p>
              </div>
            ) : (
              establishments.map((est) => (
                <div key={est.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <h3 className="text-xl font-semibold text-green-800 mb-2">{est.name}</h3>
                  <div className="space-y-2 text-gray-600">
                    <p><span className="font-medium">SIRET:</span> {est.siret}</p>
                    <p><span className="font-medium">Adresă:</span> {est.address}</p>
                    <p><span className="font-medium">Suprafață:</span> {est.surface_ha} ha</p>
                  </div>
                  <div className="mt-4 pt-4 border-t">
                    <button className="text-green-600 hover:text-green-700 font-semibold">
                      Vezi parcele →
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}