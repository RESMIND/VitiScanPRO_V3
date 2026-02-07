'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { authzAPI } from '@/lib/api';

// Lazy load the map to avoid SSR issues
const ParcelMap = dynamic(() => import('@/components/ParcelMap'), {
  ssr: false,
  loading: () => <div className="w-full h-[600px] bg-gray-200 rounded-lg animate-pulse" />
});

interface ParcelData {
  id: string;
  name: string;
  coordinates: number[][][];
  surface_ha: number;
  crop_type?: string;
  establishment_id?: string;
}

export default function ViewTokenPage() {
  const params = useParams();
  const token = params?.token as string;

  const [parcel, setParcel] = useState<ParcelData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tokenInfo, setTokenInfo] = useState<any>(null);

  useEffect(() => {
    if (token) {
      verifyAndFetch();
    }
  }, [token]);

  const verifyAndFetch = async () => {
    try {
      // Step 1: Inspect token
      const tokenData = await authzAPI.inspectToken(token);
      setTokenInfo(tokenData);

      // Step 2: Fetch resource if token is valid
      const resourceData = await authzAPI.getResourceByToken(token);
      const coordinates = resourceData?.coordinates?.coordinates
        ? resourceData.coordinates.coordinates
        : resourceData.coordinates;

      setParcel({
        id: resourceData.id,
        name: resourceData.name,
        surface_ha: resourceData.surface_ha,
        crop_type: resourceData.crop_type,
        establishment_id: resourceData.establishment_id,
        coordinates: coordinates || [],
      });
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Token invalid sau expirat';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificare token...</p>
        </div>
      </div>
    );
  }

  if (error || !parcel) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Token Invalid
          </h2>
          <p className="text-gray-600 mb-6">
            {error || 'Token-ul a expirat, a fost revocat sau este invalid.'}
          </p>
          <div className="text-sm text-gray-500">
            Dacă crezi că aceasta este o eroare, contactează proprietarul resursei.
          </div>
        </div>
      </div>
    );
  }

  const expiresAt = tokenInfo?.expires_at ? new Date(tokenInfo.expires_at) : null;
  const timeRemaining = expiresAt ? Math.max(0, Math.floor((expiresAt.getTime() - Date.now()) / 1000 / 60 / 60)) : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Warning Banner */}
      <div className="bg-yellow-50 border-b border-yellow-200 py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span className="text-sm font-medium text-yellow-800">
                🔐 Vizualizare Read-Only cu Token Temporar
              </span>
            </div>
            <div className="text-xs text-yellow-700">
              Expiră în <strong>{timeRemaining}h</strong>
              {tokenInfo?.max_uses && tokenInfo?.uses_count !== undefined && (
                <> • Utilizări: <strong>{tokenInfo.uses_count}/{tokenInfo.max_uses}</strong></>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {parcel.name}
              </h1>
              <p className="text-gray-600">
                Parcelle partagée temporairement pour la visualisation
              </p>
            </div>
            <div className="flex flex-col items-end">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-300">
                👁️ READ ONLY
              </span>
            </div>
          </div>
        </div>

        {/* Parcel Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Suprafață</div>
            <div className="text-2xl font-bold text-gray-900">{parcel.surface_ha} ha</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Tip Cultură</div>
            <div className="text-2xl font-bold text-gray-900">{parcel.crop_type || 'Necunoscut'}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">ID Parcelle</div>
            <div className="text-lg font-mono text-gray-900 truncate">{parcel.id}</div>
          </div>
        </div>

        {/* Map */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            📍 Localizare
          </h2>
          <ParcelMap
            parcels={[parcel]}
            editable={false}
            center={parcel.coordinates[0][0] ? [parcel.coordinates[0][0][1], parcel.coordinates[0][0][0]] as [number, number] : undefined}
            zoom={15}
          />
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex">
            <svg className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-2">📌 Despre acest acces:</p>
              <ul className="space-y-1 text-blue-800">
                <li>• Vous avez reçu un accès temporaire à cette parcelle</li>
                <li>• Poți vizualiza informațiile și harta, dar nu poți edita</li>
                <li>• Token-ul va expira automat după perioada specificată</li>
                <li>• Pentru acces complet, contactează proprietarul parcelei</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Powered by VitiScan • Capability Token Access</p>
        </div>
      </div>
    </div>
  );
}
