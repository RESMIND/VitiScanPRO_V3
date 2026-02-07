'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ErrorAlert } from '@/components/UIComponents';
import { establishmentsAPI, parcelsAPI, scansAPI } from '@/lib/api';

interface Parcel {
  id: string;
  name: string;
  establishment_id: string;
}

function NewScanPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedParcelId = searchParams?.get('parcel_id');

  const [formData, setFormData] = useState({
    parcel_id: preselectedParcelId || '',
    scan_date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [loadingParcels, setLoadingParcels] = useState(true);

  useEffect(() => {
    const loadParcels = async () => {
      try {
        setError('');
        const establishments = await establishmentsAPI.getMine();
        if (!establishments || establishments.length === 0) {
          setParcels([]);
          return;
        }

        const parcelsByEstablishment = await Promise.all(
          establishments.map((est: any) => parcelsAPI.getByEstablishment(est.id))
        );

        const allParcels = parcelsByEstablishment.flat().map((parcel: any) => ({
          id: parcel.id,
          name: parcel.name,
          establishment_id: parcel.establishment_id,
        }));

        setParcels(allParcels);
      } catch (err: any) {
        const message = err?.response?.data?.detail || err?.message || 'Eroare la încărcarea parcelelor';
        setError(message);
      } finally {
        setLoadingParcels(false);
      }
    };

    loadParcels();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      setError('Vă rugăm să selectați un fișier valid (JPG, PNG, PDF)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Imaginea este prea mare. Maximum 10MB');
      return;
    }

    setSelectedFile(file);
    setError('');

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.parcel_id) {
      setError('Sélectionnez une parcelle');
      return;
    }

    if (!selectedFile) {
      setError('Selectează o imagine pentru scanare');
      return;
    }

    setUploading(true);
    setError('');
    setUploadProgress(0);

    try {
      // Simulate progress (since fetch doesn't support progress events)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      await scansAPI.upload(formData.parcel_id, selectedFile);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setSuccess(true);

      // Redirect after 2 seconds
      setTimeout(() => {
        router.push(`/parcels/${formData.parcel_id}`);
      }, 2000);

    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Eroare la încărcarea scanării';
      setError(message);
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Scanare Încărcată!</h2>
          <p className="text-gray-600 mb-4">
            Imaginea a fost încărcată cu succes și va fi analizată în curând.
          </p>
          <p className="text-sm text-gray-500">Redirecționare...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <button onClick={() => router.back()} className="text-gray-600 hover:text-gray-900">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📸 Scanare Nouă</h1>
              <p className="text-sm text-gray-600">Încarcă o imagine pentru analiză</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
          {/* Parcel Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parcelle *
            </label>
            <select
              required
              value={formData.parcel_id}
              onChange={(e) => setFormData({ ...formData, parcel_id: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={!!preselectedParcelId}
            >
              <option value="">Sélectionnez la parcelle</option>
              {loadingParcels ? (
                <option value="" disabled>Chargement des parcelles...</option>
              ) : parcels.length === 0 ? (
                <option value="" disabled>Nu există parcele</option>
              ) : (
                parcels.map((parcel) => (
                  <option key={parcel.id} value={parcel.id}>{parcel.name}</option>
                ))
              )}
            </select>
          </div>

          {/* Scan Date */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Scanării *
            </label>
            <input
              type="date"
              required
              value={formData.scan_date}
              onChange={(e) => setFormData({ ...formData, scan_date: e.target.value })}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          {/* Image Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Imagine *
            </label>
            
            {!preview ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-6xl mb-4">📸</div>
                  <p className="text-gray-600 mb-2">Click pentru a selecta o imagine</p>
                  <p className="text-sm text-gray-500">sau drag & drop aici</p>
                  <p className="text-xs text-gray-400 mt-2">PNG, JPG până la 10MB</p>
                </label>
              </div>
            ) : (
              <div className="relative">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-64 object-cover rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview('');
                  }}
                  className="absolute top-2 right-2 bg-red-600 text-white p-2 rounded-full hover:bg-red-700"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <div className="mt-2 text-sm text-gray-600">
                  {selectedFile?.name} ({(selectedFile!.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              </div>
            )}
          </div>

          {/* Notes */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notițe (opțional)
            </label>
            <textarea
              rows={4}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Observații despre această scanare..."
            />
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Încărcare...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error */}
          {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

          {/* Submit */}
          <button
            type="submit"
            disabled={uploading || !selectedFile}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? 'Chargement...' : 'Télécharger l\'analyse'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function NewScanPageWrapper() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <NewScanPage />
    </Suspense>
  );
}
