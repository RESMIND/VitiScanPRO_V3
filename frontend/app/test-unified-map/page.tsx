'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

const UnifiedMapModal = dynamic(() => import('../../src/components/UnifiedMapModal'), {
  ssr: false,
  loading: () => <div>Loading map...</div>
});

export default function TestUnifiedMap() {
  const [isOpen, setIsOpen] = useState(false);

  // Mock data for testing
  const mockUser = {
    id: 1,
    name: "Test Viticulteur",
    establishment: "Domaine Test"
  };

  const mockParcels = [
    {
      id: "parcel-1",
      name: "LES GRAVES",
      crop_type: "Grenache",
      area_ha: 2.5,
      planting_year: 2015,
      geometry: {
        type: "Polygon",
        coordinates: [[
          [4.9251, 44.3341], [4.9261, 44.3351],
          [4.9271, 44.3341], [4.9261, 44.3331],
          [4.9251, 44.3341]
        ]]
      }
    },
    {
      id: "parcel-2",
      name: "LA COLLINE",
      crop_type: "Syrah",
      area_ha: 1.8,
      planting_year: 2012,
      geometry: {
        type: "Polygon",
        coordinates: [[
          [4.9351, 44.3441], [4.9361, 44.3451],
          [4.9371, 44.3441], [4.9361, 44.3431],
          [4.9351, 44.3441]
        ]]
      }
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          🗺️ Test Hartă Unificată VitiScan
        </h1>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <p className="text-blue-800">
            <strong>📍 Locație:</strong> Harta se deschide centrată pe Sainte-Cécile-les-Vignes (84290), Franța
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Funcționalități de Testat:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h3 className="font-medium text-gray-900">🎨 Moduri Vizuale:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Colorare pe soiuri (🎨)</li>
                <li>• Mod planificare (📅)</li>
                <li>• Overlay NDVI (👁️)</li>
                <li>• Overlay meteo (🌡️)</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium text-gray-900">🛡️ Funcții ZNT:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Strat BCAE PAC (🛡️)</li>
                <li>• Zone tampon</li>
                <li>• Verificare conformitate</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium text-gray-900">🗺️ Controale Hartă:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Straturi bază (OSM, IGN)</li>
                <li>• 🔍 Căutare cadastrală (PACA)</li>
                <li>• Zoom și pan</li>
                <li>• Fullscreen (⛶)</li>
                <li>• Popup parcele</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium text-gray-900">📊 Panel Lateral:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Legendă soiuri</li>
                <li>• Statistici planificare</li>
                <li>• Scală NDVI</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">
            🚀 Lansare Test
          </h2>
          <p className="text-blue-800 mb-4">
            Click pe butonul de mai jos pentru a deschide harta unificată cu date de test.
          </p>
          <button
            onClick={() => setIsOpen(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
          >
            🗺️ Deschide Hartă Unificată
          </button>
        </div>

        <UnifiedMapModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          user={mockUser}
          parcels={mockParcels as any}
          onParcelDrawn={null}
          onSearchComplete={null}
        />
      </div>
    </div>
  );
}