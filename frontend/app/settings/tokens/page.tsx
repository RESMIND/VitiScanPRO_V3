'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert, SuccessAlert, EmptyState } from '@/components/UIComponents';
import { authzAPI } from '@/lib/api';

interface Token {
  id: string;
  resource_id: string;
  resource_type: string;
  permission: 'view' | 'share';
  created_at: string;
  expires_at?: string;
  used_count: number;
  max_uses?: number | null;
}

export default function TokensSettingsPage() {
  const router = useRouter();
  const [tokens, setTokens] = useState<Token[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'expired'>('active');

  useEffect(() => {
    loadTokens();
  }, []);

  const loadTokens = async () => {
    try {
      const data = await authzAPI.listTokens();
      const mapped = (data?.tokens || []).map((t: any) => ({
        id: t._id || t.id,
        resource_id: t.resource_id,
        resource_type: t.resource_type,
        permission: t.action === 'read' ? 'view' : 'share',
        created_at: t.created_at,
        expires_at: t.expires_at,
        used_count: t.used_count || 0,
        max_uses: t.max_uses ?? null,
      })) as Token[];

      setTokens(mapped);
    } catch (error) {
      console.error('Error loading tokens:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea tokens';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeToken = async (tokenId: string) => {
    if (!confirm('Sigur vrei să revoci acest token? Acest lucru nu poate fi anulat.')) {
      return;
    }

    try {
      await authzAPI.revokeTokenById(tokenId);

      setSuccess('Token revocat cu succes!');
      await loadTokens();
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Eroare la revocare token';
      setError(message);
    }
  };

  const isExpired = (token: Token) => {
    if (!token.expires_at) return false;
    return new Date(token.expires_at) < new Date();
  };

  const filteredTokens = tokens.filter(token => {
    if (filter === 'active') return !isExpired(token);
    if (filter === 'expired') return isExpired(token);
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Setări', href: '/settings/profile' },
          { label: 'Capability Tokens' }
        ]} />

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Capability Tokens</h1>
          <p className="text-gray-600 mt-2">Gestionează token-urile de partajare pentru parcelele tale</p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess('')} />}

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <div className="text-2xl">ℹ️</div>
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">Ce sunt Capability Tokens?</h3>
              <p className="text-sm text-blue-800">
                Capability tokens îți permit să partajezi acces la parcelele tale cu alți utilizatori fără a le oferi acces complet la contul tău. 
                Există două tipuri: <strong>View</strong> (doar vizualizare) și <strong>Share</strong> (vizualizare + partajare cu alții).
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Total Tokens</div>
            <div className="text-2xl font-bold text-gray-900">{tokens.length}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Active</div>
            <div className="text-2xl font-bold text-green-600">
              {tokens.filter(t => !isExpired(t)).length}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Expirate / Revocate</div>
            <div className="text-2xl font-bold text-red-600">
              {tokens.filter(t => isExpired(t)).length}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filtrare:</span>
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Toate ({tokens.length})
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'active'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Active ({tokens.filter(t => !isExpired(t)).length})
            </button>
            <button
              onClick={() => setFilter('expired')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'expired'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Expirate ({tokens.filter(t => isExpired(t)).length})
            </button>
          </div>
        </div>

        {/* Tokens List */}
        {filteredTokens.length === 0 ? (
          <EmptyState
            icon="🔐"
            title="Nu există tokens"
            description="Creează un token de partajare din pagina unei parcele"
            action={{
              label: "Vezi Parcele",
              onClick: () => router.push('/parcels')
            }}
          />
        ) : (
          <div className="space-y-4">
            {filteredTokens.map((token) => {
              const expired = isExpired(token);

              return (
                <div
                  key={token.id}
                  className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {token.resource_type} {token.resource_id.substring(0, 8)}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          token.permission === 'view'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          {token.permission === 'view' ? '👁️ View' : '🔗 Share'}
                        </span>
                        {!expired ? (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            ✅ Activ
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                            ⏰ Expirat
                          </span>
                        )}
                      </div>

                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <span>Creat:</span>
                          <span className="text-gray-900">
                            {new Date(token.created_at).toLocaleDateString('ro-RO')}
                          </span>
                        </div>
                        {token.expires_at && (
                          <div className="flex items-center space-x-2">
                            <span>Expiră:</span>
                            <span className={expired ? 'text-red-600 font-medium' : 'text-gray-900'}>
                              {new Date(token.expires_at).toLocaleDateString('ro-RO')}
                            </span>
                          </div>
                        )}
                        <div className="flex items-center space-x-2">
                          <span>Utilizări:</span>
                          <span className="text-gray-900">
                            {token.used_count}{token.max_uses ? ` / ${token.max_uses}` : ''}
                          </span>
                        </div>
                      </div>

                      <div className="mt-3 text-xs text-gray-500 bg-gray-50 border border-gray-200 rounded-lg p-3">
                        Token-ul brut nu este stocat și nu poate fi reafișat. Pentru un link nou, generează un token nou din pagina parcelei.
                      </div>
                    </div>

                    {!expired && (
                      <button
                        onClick={() => handleRevokeToken(token.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Revocă
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Help Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Cum să creez un token nou?</h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
            <li>Allez à la page d'une <Link href="/parcels" className="text-green-600 hover:underline">parcelle</Link></li>
            <li>Click pe butonul "Partajează" (🔗)</li>
            <li>Alege tipul de permisiune (View sau Share)</li>
            <li>Setează data de expirare (opțional)</li>
            <li>Generează token și copiază linkul</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
