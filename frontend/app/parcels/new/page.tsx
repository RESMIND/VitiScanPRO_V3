'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { establishmentsAPI, parcelsAPI } from '@/lib/api';

// Import UnifiedMapModal for enhanced parcel creation workflow
const UnifiedMapModal = dynamic(() => import('../../../src/components/UnifiedMapModal'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-gray-200 rounded-lg flex items-center justify-center">
      <p className="text-gray-600">Chargement de la carte...</p>
    </div>
  ),
});

interface EstablishmentOption {
  id: string;
  name: string;
}

export default function ParcelMapPage() {
  const router = useRouter();
  const [parcelData, setParcelData] = useState({
    name: '',
    crop_type: '',
    planting_year: '' as number | '',
    area_ha: 0,
    coordinates: [] as number[][][],
    soil_analysis: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [establishments, setEstablishments] = useState<EstablishmentOption[]>([]);
  const [establishmentId, setEstablishmentId] = useState('');
  const [establishmentsLoading, setEstablishmentsLoading] = useState(false);
  const [isMapOpen, setIsMapOpen] = useState(true);
  const [currentStep, setCurrentStep] = useState<'search' | 'draw' | 'details'>('search');

  // Mock user data for UnifiedMapModal
  const mockUser = {
    id: 'current-user',
    name: 'Utilizator',
    establishment: 'Exploatație'
  };

  const toErrorMessage = (err: any) => {
    const detail = err?.response?.data?.detail;
    if (!detail) return err?.message || 'Eroare la crearea parcelei';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) => item?.msg || item?.message || JSON.stringify(item))
        .join('; ');
    }
    if (typeof detail === 'object') {
      return detail?.msg || JSON.stringify(detail);
    }
    return String(detail);
  };

  const handleParcelDrawn = (coordinates: number[][][], area: number) => {
    setParcelData({
      ...parcelData,
      coordinates,
      area_ha: area,
    });
    setSuccess(false);
    setCurrentStep('details');
    setShowDetailsModal(true);
  };

  const handleSearchComplete = () => {
    setCurrentStep('draw');
  };

  useEffect(() => {
    const loadEstablishments = async () => {
      setEstablishmentsLoading(true);
      try {
        const data = await establishmentsAPI.getMine();
        setEstablishments(data || []);
        if (data && data.length > 0) {
          setEstablishmentId(data[0].id);
        }
      } catch (err: any) {
        setError(toErrorMessage(err));
      } finally {
        setEstablishmentsLoading(false);
      }
    };

    loadEstablishments();
  }, []);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setError('');
    setLoading(true);

    if (!parcelData.coordinates || parcelData.coordinates.length === 0) {
      setError('Vous devez tracer la parcelle sur la carte!');
      setLoading(false);
      return;
    }

    if (!establishmentId) {
      setError('Sélectionnez l\'établissement pour la parcelle.');
      setLoading(false);
      return;
    }

    try {
      const plantingYearValue = parcelData.planting_year === '' ? undefined : parcelData.planting_year;
      await parcelsAPI.create({
        name: parcelData.name,
        crop_type: parcelData.crop_type,
        area_ha: parcelData.area_ha,
        establishment_id: establishmentId,
        coordinates: parcelData.coordinates,
        planting_year: plantingYearValue,
      });

      setSuccess(true);
      setShowDetailsModal(false);
      setParcelData({
        name: '',
        crop_type: '',
        planting_year: '' as number | '',
        area_ha: 0,
        coordinates: [],
        soil_analysis: '',
        notes: '',
      });

      // Redirect after 2 seconds
      setTimeout(() => {
        router.back();
      }, 2000);
    } catch (err: any) {
      setError(toErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-900">
      {/* Unified Map Modal for enhanced parcel creation */}
      <UnifiedMapModal
        isOpen={isMapOpen}
        onClose={() => router.back()}
        user={mockUser}
        parcels={[]}
        onParcelDrawn={handleParcelDrawn}
        onSearchComplete={handleSearchComplete}
        creationMode={true}
        currentStep={currentStep}
      />

      {/* Instructions Panel */}
      <div className="fixed top-4 left-4 z-[500] max-w-sm rounded-lg bg-white/95 backdrop-blur border border-gray-200 shadow-lg p-4">
        <button
          onClick={() => router.back()}
          className="text-green-700 hover:text-green-800 flex items-center gap-2 text-sm font-medium"
        >
          ← Înapoi
        </button>
        <h1 className="mt-3 text-xl font-bold text-gray-900">Creare parcelă nouă</h1>
        
        <div className="mt-3 space-y-2">
          <div className={`p-2 rounded ${currentStep === 'search' ? 'bg-blue-100 border border-blue-300' : 'bg-gray-50'}`}>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-full ${currentStep === 'search' ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
              <span className="text-sm font-medium">1. Caută parcela cadastrală</span>
            </div>
          </div>
          
          <div className={`p-2 rounded ${currentStep === 'draw' ? 'bg-blue-100 border border-blue-300' : 'bg-gray-50'}`}>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-full ${currentStep === 'draw' ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
              <span className="text-sm font-medium">2. Desenează parcela exact</span>
            </div>
          </div>
          
          <div className={`p-2 rounded ${currentStep === 'details' ? 'bg-blue-100 border border-blue-300' : 'bg-gray-50'}`}>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-full ${currentStep === 'details' ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
              <span className="text-sm font-medium">3. Completează detaliile</span>
            </div>
          </div>
        </div>

        <div className="mt-3 rounded-lg bg-blue-50 border border-blue-200 p-3">
          <h3 className="font-semibold text-blue-800 mb-1 text-sm">📍 Instrucțiuni</h3>
          <div className="text-xs text-blue-700 space-y-1">
            {currentStep === 'search' && (
              <div>
                <p>• Caută comuna și referința cadastrală</p>
                <p>• Selectează parcela din rezultate</p>
              </div>
            )}
            {currentStep === 'draw' && (
              <div>
                <p>• Schimbă la strat satelit</p>
                <p>• Desenează poligonul exact al parcelei</p>
                <p>• Punctele intermediare apar automat</p>
              </div>
            )}
            {currentStep === 'details' && (
              <div>
                <p>• Completează toate detaliile parcelei</p>
                <p>• Adaugă analize sol și note</p>
              </div>
            )}
          </div>
        </div>

        {parcelData.coordinates.length > 0 && (
          <div className="mt-3 rounded-lg bg-green-50 border border-green-200 p-3">
            <p className="text-green-800 text-sm font-semibold">
              ✓ Parcela desenată: {parcelData.area_ha} ha
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="fixed top-4 right-4 z-[500] max-w-sm bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded shadow">
          {error}
        </div>
      )}

      {success && (
        <div className="fixed top-4 right-4 z-[500] max-w-sm bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded shadow">
          Parcelle créée avec succès ! Redirection...
        </div>
      )}

      {showDetailsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Detalii parcelă</h2>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Închide"
              >
                ✕
              </button>
            </div>

            <form onSubmit={(e) => handleSubmit(e)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Exploatație *
                  </label>
                  <select
                    value={establishmentId}
                    onChange={(e) => setEstablishmentId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-green-500"
                    required
                    disabled={establishmentsLoading}
                  >
                    {establishments.length === 0 ? (
                      <option value="">Nu ai exploatații</option>
                    ) : (
                      establishments.map((est) => (
                        <option key={est.id} value={est.id}>
                          {est.name}
                        </option>
                      ))
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nume parcelă *
                  </label>
                  <input
                    type="text"
                    value={parcelData.name}
                    onChange={(e) => setParcelData({ ...parcelData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 bg-white focus:ring-2 focus:ring-green-500"
                    placeholder="ex: Parcela Nord"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tip cultură *
                  </label>
                  <select
                    value={parcelData.crop_type}
                    onChange={(e) => setParcelData({ ...parcelData, crop_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="">Selectează...</option>
                    <option value="Viță de vie">Viță de vie</option>
                    <option value="Porumb">Porumb</option>
                    <option value="Grâu">Grâu</option>
                    <option value="Floarea soarelui">Floarea soarelui</option>
                    <option value="Soia">Soia</option>
                    <option value="Rapiță">Rapiță</option>
                    <option value="Alte culturi">Alte culturi</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    An plantare
                  </label>
                  <input
                    type="number"
                    min="1900"
                    max={new Date().getFullYear()}
                    value={parcelData.planting_year}
                    onChange={(e) => {
                      const value = e.target.value;
                      setParcelData({
                        ...parcelData,
                        planting_year: value === '' ? '' : parseInt(value, 10),
                      });
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 bg-white focus:ring-2 focus:ring-green-500"
                    placeholder="ex: 2012"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Analize sol
                </label>
                <textarea
                  value={parcelData.soil_analysis}
                  onChange={(e) => setParcelData({ ...parcelData, soil_analysis: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 bg-white focus:ring-2 focus:ring-green-500"
                  placeholder="ex: pH 7.2, Azot total 0.15%, Fosfor 45 ppm, Potasiu 180 ppm..."
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Note suplimentare
                </label>
                <textarea
                  value={parcelData.notes}
                  onChange={(e) => setParcelData({ ...parcelData, notes: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 bg-white focus:ring-2 focus:ring-green-500"
                  placeholder="Note despre parcelă, particularități, observații..."
                  rows={3}
                />
              </div>

              <div className="flex items-center justify-between pt-4 border-t">
                <div className="text-sm text-gray-600">
                  <div>Suprafață: <span className="font-semibold text-gray-900">{parcelData.area_ha} ha</span></div>
                  <div>Perimetru: <span className="font-semibold text-gray-900">Calculat automat</span></div>
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowDetailsModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Anulează
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !parcelData.coordinates.length}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                  >
                    {loading ? 'Se salvează...' : 'Salvează parcela'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
