'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { establishmentsAPI, parcelsAPI } from '@/lib/api';
import ParcelQuickCard from '@/components/ParcelQuickCard';

const ParcelMap = dynamic(() => import('@/components/ParcelMap'), {
  ssr: false,
  loading: () => <div className="w-full h-screen bg-gray-200 flex items-center justify-center">Chargement de la carte...</div>
});

interface ParcelData {
  id: string;
  name: string;
  crop_type?: string;
  area_ha: number;
  coordinates: number[][][];
  establishment_id?: string;
}

interface Establishment {
  id: string;
  name: string;
}

export default function ParcelsMapPage() {
  const router = useRouter();
  const [parcels, setParcels] = useState<ParcelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedParcel, setSelectedParcel] = useState<ParcelData | null>(null);

  useEffect(() => {
    loadParcels();
  }, []);

  const loadParcels = async () => {
    setLoading(true);
    try {
      const establishments: Establishment[] = await establishmentsAPI.getMine();
      if (!establishments || establishments.length === 0) {
        setParcels([]);
        setLoading(false);
        return;
      }

      const parcelsByEst = await Promise.all(
        establishments.map((est: Establishment) => parcelsAPI.getByEstablishment(est.id))
      );

      const allParcels = parcelsByEst.flat().map((p: any) => ({
        id: p.id,
        name: p.name,
        crop_type: p.crop_type,
        area_ha: p.area_ha || p.surface_ha,
        coordinates: p.coordinates
      })) as ParcelData[];

      setParcels(allParcels);
    } catch (err: any) {
      setError('Eroare la încărcarea parcelelor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleParcelClick = (parcelId: string) => {
    const parcel = parcels.find(p => p.id === parcelId);
    if (parcel) {
      setSelectedParcel(parcel);
    }
  };

  return (
    <div className="relative w-full h-screen">
      {/* Map */}
      <ParcelMap
        parcels={parcels}
        onParcelClick={handleParcelClick}
        editable={false}
        center={[43.9493, 4.8055]}
        zoom={10}
        mapClassName="w-full h-full"
      />

      {/* Loading State */}
      {loading && (
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto mb-3"></div>
            <p className="text-gray-700">Chargement des parcelles...</p>
          </div>
        </div>
      )}

      {/* Back Button */}
      <button
        onClick={() => router.push('/dashboard')}
        className="absolute top-4 left-4 bg-white hover:bg-gray-100 text-gray-800 px-4 py-2 rounded-lg shadow-lg transition-colors z-30"
      >
        ← Dashboard
      </button>

      {/* Quick Card Modal */}
      {selectedParcel && (
        <ParcelQuickCard
          parcelId={selectedParcel.id}
          parcelName={selectedParcel.name}
          cropType={selectedParcel.crop_type}
          areaHa={selectedParcel.area_ha}
          coordinates={selectedParcel.coordinates}
          onClose={() => setSelectedParcel(null)}
        />
      )}
    </div>
  );
}
