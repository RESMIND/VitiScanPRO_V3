'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { parcelsAPI } from '@/lib/api';

interface Parcel {
  id: string;
  name: string;
  establishment_id?: string;
  crop_type?: string;
  area_ha: number;
  coordinates?: number[][][];
  planting_year?: number;
  created_at?: string;
}

export default function ParcelDetailPage() {
  const router = useRouter();
  const params = useParams();
  const parcelId = params?.id as string;

  const [parcel, setParcel] = useState<Parcel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Calculate centroid of polygon
  const calculateCentroid = (coordinates: any) => {
    if (!coordinates) return null;
    
    // Handle GeoJSON format: { type: "Polygon", coordinates: [...] }
    let coords = coordinates;
    if (coordinates && coordinates.coordinates) {
      coords = coordinates.coordinates;
    }
    
    if (!coords || !Array.isArray(coords) || coords.length === 0) return null;
    
    const ring = coords[0];
    if (!ring || !Array.isArray(ring) || ring.length === 0) return null;
    
    let x = 0, y = 0;
    const len = ring.length - 1; // Exclude last point (same as first)
    for (let i = 0; i < len; i++) {
      x += ring[i][0];
      y += ring[i][1];
    }
    return { lng: x / len, lat: y / len };
  };

  useEffect(() => {
    if (parcelId) {
      loadParcel();
    }
  }, [parcelId]);

  const loadParcel = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('Loading parcel:', parcelId);
      const data = await parcelsAPI.getById(parcelId);
      console.log('Parcel data received:', data);
      console.log('Parcel data type:', typeof data);
      console.log('Parcel coordinates:', data?.coordinates);
      setParcel(data);
    } catch (err: any) {
      console.error('Error loading parcel:', err);
      setError('La parcelle n\'a pas été trouvée');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Chargement...</p>
        </div>
      </div>
    );
  }

  if (error || !parcel) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 max-w-md w-full text-center">
          <div className="text-red-500 text-5xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-white mb-2">Parcelle non trouvée</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <div className="flex flex-col gap-3">
            <Link href="/parcels/map" className="text-blue-500 hover:text-blue-400 font-medium">
              Aller à la Carte des Parcelles →
            </Link>
            <Link href="/dashboard" className="text-green-500 hover:text-green-400 font-medium">
              ← Retour au Tableau de bord
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const centroid = calculateCentroid(parcel.coordinates);

  // Sidebar Cards
  const SoilCard = () => (
    <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-4 cursor-pointer hover:from-green-800 hover:to-green-700 transition-all border border-green-700">
      <div className="flex items-center gap-3">
        <div className="text-2xl">🧪</div>
        <div>
          <h3 className="text-white font-semibold text-sm">Sol</h3>
          <p className="text-green-200 text-xs">Téléchargement nouveau</p>
        </div>
      </div>
    </div>
  );

  const HistoryCard = () => (
    <div className="bg-gradient-to-br from-amber-900 to-amber-800 rounded-lg p-4 cursor-pointer hover:from-amber-800 hover:to-amber-700 transition-all border border-amber-700">
      <div className="flex items-center gap-3">
        <div className="text-2xl">📋</div>
        <div>
          <h3 className="text-white font-semibold text-sm">Historique</h3>
          <p className="text-amber-200 text-xs">Sol analize</p>
        </div>
      </div>
    </div>
  );

  const ProdCard = () => (
    <div className="bg-gradient-to-br from-teal-900 to-teal-800 rounded-lg p-4 cursor-pointer hover:from-teal-800 hover:to-teal-700 transition-all border border-teal-700">
      <div className="flex items-center gap-3">
        <div className="text-2xl">📈</div>
        <div>
          <h3 className="text-white font-semibold text-sm">Prod.</h3>
          <p className="text-teal-200 text-xs">Afficher</p>
        </div>
      </div>
    </div>
  );

  const DiagnosticsCard = () => (
    <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg p-4 cursor-pointer hover:from-blue-800 hover:to-blue-700 transition-all border border-blue-700">
      <div className="flex items-center gap-3">
        <div className="text-2xl">🔬</div>
        <div>
          <h3 className="text-white font-semibold text-sm">Diagnostics AI</h3>
          <p className="text-blue-200 text-xs">{parcel.name}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="text-green-500 hover:text-green-400 text-2xl transition-colors"
        >
          ←
        </button>
        <div>
          <h1 className="text-3xl font-bold text-white">{parcel.name}</h1>
          <p className="text-gray-400 text-sm mt-1">{parcel.area_ha} ha • {parcel.crop_type || 'Nespecificat'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar */}
        <div className="space-y-4">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <h3 className="text-white text-sm font-semibold mb-2">ID Parcelle</h3>
            <p className="text-gray-400 text-xs font-mono break-all">{parcel.id.substring(0, 12)}...</p>
          </div>

          {parcel.planting_year && (
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <h3 className="text-white text-sm font-semibold mb-2">📅 Anul Plantării</h3>
              <p className="text-gray-300 text-lg font-bold">{parcel.planting_year}</p>
            </div>
          )}
        </div>

        {/* Center - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* GPS & Centroid Card */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h2 className="text-white font-semibold mb-4 flex items-center gap-2">🗺️ Coordonnées GPS</h2>

            {centroid && (
              <div className="bg-gray-900 rounded p-4 mb-4 border border-gray-600">
                <div className="text-sm text-gray-400 mb-3">Centroid (Centrul parcelei)</div>
                <div className="space-y-2">
                  <div>
                    <div className="text-xs text-gray-500">Latitudine</div>
                    <div className="text-lg font-mono text-green-400">
                      {centroid.lat.toFixed(6)}° N
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Longitudine</div>
                    <div className="text-lg font-mono text-green-400">
                      {centroid.lng.toFixed(6)}° E
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Operator/Contractor Redirect */}
            <div className="space-y-3">
              <h3 className="text-sm text-gray-300 font-semibold">Redirectioneaza catre:</h3>
              <div className="grid grid-cols-2 gap-2">
                <button className="bg-blue-600 hover:bg-blue-700 text-white text-xs py-2 px-3 rounded transition-colors font-semibold">
                  👤 Operator
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 text-white text-xs py-2 px-3 rounded transition-colors font-semibold">
                  🔧 Prestatar
                </button>
              </div>
            </div>
          </div>

          {/* Calendar Placeholder */}
          <div className="bg-gradient-to-br from-pink-900 to-pink-800 rounded-lg p-6 cursor-pointer hover:from-pink-800 hover:to-pink-700 transition-all border border-pink-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold flex items-center gap-2">
                📅 Calendrier & Événements
              </h3>
              <span className="text-2xl">→</span>
            </div>
            <p className="text-pink-200 text-sm">
              Fonctionnalité en développement. Revenez bientôt !
            </p>
          </div>
        </div>

        {/* Right Sidebar - Menu Actions */}
        <div className="space-y-3">
          <SoilCard />
          <HistoryCard />
          <ProdCard />
          <DiagnosticsCard />
        </div>
      </div>
    </div>
  );
}
