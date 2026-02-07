'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { authzAPI } from '@/lib/api';

export default function ShareParcelPage() {
  const params = useParams();
  const router = useRouter();
  const parcelId = params?.id as string;

  const [formData, setFormData] = useState({
    valid_hours: 24,
    max_uses: 0,
    target_subject: ''
  });
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setToken('');

    try {
      const data = await authzAPI.createToken({
        resource_type: 'parcel',
        resource_id: parcelId,
        action: 'view',
        expires_in_hours: formData.valid_hours,
        max_uses: formData.max_uses > 0 ? formData.max_uses : null,
        subject_id: formData.target_subject || undefined,
      });
      setToken(data.token);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Tokenul nu a putut fi generat';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    const url = `${window.location.origin}/view/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="text-green-600 hover:text-green-700 mb-4 flex items-center"
          >
            ← Retour
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🔐 Share Parcel
          </h1>
          <p className="text-gray-600">
            Generează un link temporar pentru vizualizarea parcelei <strong>{parcelId}</strong>
          </p>
        </div>

        {!token ? (
          /* Token Generation Form */
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">
              Configurare Token
            </h2>

            <div className="space-y-6">
              {/* Valid Hours */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Valabilitate (ore)
                </label>
                <select
                  value={formData.valid_hours}
                  onChange={(e) => setFormData({ ...formData, valid_hours: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value={1}>1 oră</option>
                  <option value={6}>6 ore</option>
                  <option value={24}>24 ore (1 zi)</option>
                  <option value={72}>3 zile</option>
                  <option value={168}>7 zile</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Token-ul va expira după această perioadă
                </p>
              </div>

              {/* Max Uses */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Număr maxim de utilizări
                </label>
                <input
                  type="number"
                  min={0}
                  value={formData.max_uses}
                  onChange={(e) => setFormData({ ...formData, max_uses: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="0 = nelimitat"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Lasă 0 pentru utilizări nelimitate în perioada de valabilitate
                </p>
              </div>

              {/* Target Subject (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User ID Specific (opțional)
                </label>
                <input
                  type="text"
                  value={formData.target_subject}
                  onChange={(e) => setFormData({ ...formData, target_subject: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="consultant_123"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Lasă gol pentru a permite oricui cu link-ul
                </p>
              </div>

              {/* Info Box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Securitate:</p>
                    <ul className="space-y-1 text-xs">
                      <li>• Token-ul este unic și poate fi folosit doar pentru vizualizare (read-only)</li>
                      <li>• Poate fi revocat oricând din secțiunea de management</li>
                      <li>• Este stocat criptat cu SHA256 în baza de date</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Se generează...' : '🔑 Generează Token'}
              </button>
            </div>
          </div>
        ) : (
          /* Token Display (Show Once) */
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Token Generat!
              </h2>
              <p className="text-gray-600 text-sm">
                Copiază link-ul de mai jos. Acesta va fi afișat doar ACUM.
              </p>
            </div>

            {/* Token Display */}
            <div className="bg-gray-50 border-2 border-green-300 rounded-lg p-4 mb-4">
              <div className="text-xs text-gray-600 mb-2 font-medium">Link de Partajare:</div>
              <div className="font-mono text-sm text-gray-900 break-all bg-white p-3 rounded border border-gray-200">
                {window.location.origin}/view/{token}
              </div>
            </div>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${
                copied
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
              }`}
            >
              {copied ? '✅ Copiat în Clipboard!' : '📋 Copiază Link'}
            </button>

            {/* Token Details */}
            <div className="mt-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Valabilitate:</span>
                <span className="font-medium text-gray-900">{formData.valid_hours} ore</span>
              </div>
              {formData.max_uses > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Utilizări maxime:</span>
                  <span className="font-medium text-gray-900">{formData.max_uses}</span>
                </div>
              )}
              {formData.target_subject && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Restricționat la:</span>
                  <span className="font-medium text-gray-900">{formData.target_subject}</span>
                </div>
              )}
            </div>

            {/* Warning */}
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div className="text-sm text-yellow-800">
                  <p className="font-medium">⚠️ Important:</p>
                  <p className="mt-1 text-xs">
                    Token-ul nu mai poate fi recuperat după închiderea acestei pagini. Asigură-te că l-ai copiat!
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex space-x-3">
              <button
                onClick={() => {
                  setToken('');
                  setFormData({ valid_hours: 24, max_uses: 0, target_subject: '' });
                }}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700"
              >
                Generează Alt Token
              </button>
              <button
                onClick={() => router.push(`/parcels/${parcelId}`)}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700"
              >
                Retour à la parcelle
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
