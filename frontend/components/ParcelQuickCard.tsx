'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface ParcelQuickCardProps {
  parcelId: string;
  parcelName: string;
  cropType?: string;
  areaHa: number;
  coordinates?: number[][][];
  onClose: () => void;
}

interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  precipitation: number;
  description: string;
}

export default function ParcelQuickCard({
  parcelId,
  parcelName,
  cropType,
  areaHa,
  coordinates,
  onClose
}: ParcelQuickCardProps) {
  const router = useRouter();
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate weather data fetch - replace with actual API call
    setTimeout(() => {
      setWeather({
        temperature: 4.4,
        humidity: 78,
        wind_speed: 0.4,
        precipitation: 0.0,
        description: 'Ciel dégagé'
      });
      setLoading(false);
    }, 500);
  }, [parcelId]);

  const handleDelete = async () => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la parcelle "${parcelName}"?`)) {
      return;
    }
    // API call would go here
    console.log('Deleting parcel:', parcelId);
    onClose();
  };

  const handleRedraw = () => {
    console.log('Redraw parcel boundary');
    // Navigate to edit page
    router.push(`/parcels/${parcelId}/edit`);
  };

  const handleCalendar = () => {
    router.push(`/parcels/${parcelId}`);
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-end justify-end p-4 z-40">
      {/* Background click to close */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Card */}
      <div className="relative bg-gray-800 rounded-lg shadow-2xl w-full max-w-sm border border-gray-700 p-6 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl"
        >
          ✕
        </button>

        {/* Header */}
        <div className="mb-6">
          <h2 className="text-white text-2xl font-bold">{parcelName}</h2>
          <p className="text-gray-400 text-sm mt-1">
            Cépage: <span className="text-gray-300">{cropType || 'Non spécifié'}</span>
          </p>
          <p className="text-gray-400 text-sm">
            Surface: <span className="text-gray-300">{areaHa} ha</span>
          </p>
        </div>

        {/* Current Weather */}
        <div className="bg-gray-900/50 rounded-lg p-4 mb-6 border border-gray-700">
          <h3 className="text-white font-semibold mb-3 text-sm">🌤️ Météo actuelle</h3>

          {loading ? (
            <div className="text-gray-400 text-sm">Chargement...</div>
          ) : weather ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-gray-400 text-xs mb-1">Température</div>
                <div className="text-white text-lg font-semibold">{weather.temperature}°C</div>
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Humidité</div>
                <div className="text-white text-lg font-semibold">{weather.humidity}%</div>
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Vent</div>
                <div className="text-white text-lg font-semibold">{weather.wind_speed} km/h</div>
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Précipitations</div>
                <div className="text-white text-lg font-semibold">{weather.precipitation} mm</div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Quick Actions */}
        <div className="space-y-2">
          <h3 className="text-white font-semibold text-sm mb-3">ACTIONS RAPIDES</h3>

          {/* Calendar & Events */}
          <button
            onClick={handleCalendar}
            className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-lg p-3 transition-all flex items-center gap-3 group"
          >
            <div className="text-xl">📅</div>
            <div className="text-left flex-1">
              <div className="font-semibold text-sm">Calendrier & Événements</div>
              <div className="text-xs text-purple-200">Traitements, récoltes</div>
            </div>
            <div className="text-lg group-hover:translate-x-1 transition-transform">›</div>
          </button>

          {/* Redraw Boundary */}
          <button
            onClick={handleRedraw}
            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg p-3 transition-all flex items-center gap-3 group"
          >
            <div className="text-xl">📍</div>
            <div className="text-left flex-1">
              <div className="font-semibold text-sm">Redessiner le contour</div>
              <div className="text-xs text-green-200">Ajuster les limites</div>
            </div>
            <div className="text-lg group-hover:translate-x-1 transition-transform">›</div>
          </button>

          {/* Delete Parcel */}
          <button
            onClick={handleDelete}
            className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-lg p-3 transition-all flex items-center gap-3 group"
          >
            <div className="text-xl">🗑️</div>
            <div className="text-left flex-1">
              <div className="font-semibold text-sm">Supprimer la parcelle</div>
              <div className="text-xs text-red-200">Action irréversible</div>
            </div>
            <div className="text-lg group-hover:translate-x-1 transition-transform">›</div>
          </button>
        </div>

        {/* Footer Info */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <p className="text-gray-500 text-xs text-center">ID: {parcelId}</p>
        </div>
      </div>
    </div>
  );
}
