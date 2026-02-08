'use client';

import { useState, useEffect, useCallback } from 'react';
import { ErrorAlert } from '@/components/UIComponents';
import { adminAPI } from '@/lib/api';

interface BetaRequest {
  id: string;
  email: string;
  phone: string;
  full_name: string;
  company?: string;
  region?: string;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  created_at: string;
  processed_at?: string;
  register_token?: string;
}

const translateStatus = (status: string) => {
  switch (status) {
    case 'pending': return 'În așteptare';
    case 'approved': return 'Aprobat';
    case 'rejected': return 'Respins';
    case 'expired': return 'Expirat';
    case 'all': return 'Toate';
    default: return status;
  }
};

export default function AdminBetaRequestsPage() {
  const [requests, setRequests] = useState<BetaRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');
  const [processing, setProcessing] = useState<string | null>(null);
  const [error, setError] = useState('');

  const extractErrorMessage = (e: unknown, fallback = 'Eroare la prelucrare') => {
    if (e instanceof Error) return e.message;
    if (typeof e === 'object' && e !== null) {
      const obj = e as Record<string, unknown>;
      const response = obj.response as Record<string, unknown> | undefined;
      const data = response?.data as Record<string, unknown> | undefined;
      const detail = data?.detail;
      if (typeof detail === 'string') return detail;
    }
    return fallback;
  };

  const fetchRequests = useCallback(async () => {
    try {
      setError('');
      const data = await adminAPI.listBetaRequests();
      const mapped = (data || []).map((req: { id?: string; email?: string; phone?: string; name?: string; full_name?: string; farm_name?: string; company?: string; region?: string; reason?: string; status?: 'pending' | 'approved' | 'rejected' | 'expired'; created_at?: string; approved_at?: string; rejected_at?: string; registration_token?: string }) => ({
        id: req.id || '',
        email: req.email || '',
        phone: req.phone || '',
        full_name: req.name || req.full_name || '',
        company: req.farm_name || req.company || undefined,
        region: req.region || undefined,
        reason: req.reason || undefined,
        status: (req.status as BetaRequest['status']) || 'pending',
        created_at: req.created_at || new Date().toISOString(),
        processed_at: req.approved_at || req.rejected_at,
        register_token: req.registration_token,
      })) as BetaRequest[];
      setRequests(mapped);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
      const message = extractErrorMessage(error, 'Eroare la încărcarea cererilor');
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const handleApprove = async (requestId: string) => {
    setProcessing(requestId);
    try {
      await adminAPI.approveBetaRequest(requestId);
      await fetchRequests();
    } catch (error) {
      console.error('Failed to approve:', error);
      const message = extractErrorMessage(error, 'Eroare la aprobarea cererii');
      setError(message);
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (requestId: string) => {
    setProcessing(requestId);
    try {
      await adminAPI.rejectBetaRequest(requestId);
      await fetchRequests();
    } catch (error) {
      console.error('Failed to reject:', error);
      const message = extractErrorMessage(error, 'Eroare la respingerea cererii');
      setError(message);
    } finally {
      setProcessing(null);
    }
  };

  const getStatusBadge = (status: BetaRequest['status']) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      approved: 'bg-green-100 text-green-800 border-green-300',
      rejected: 'bg-red-100 text-red-800 border-red-300',
      expired: 'bg-gray-100 text-gray-800 border-gray-300'
    };

    const icons = {
      pending: '⏳',
      approved: '✅',
      rejected: '❌',
      expired: '⌛'
    };

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${badges[status as keyof typeof badges]}`}>
        <span className="mr-1">{icons[status as keyof typeof icons]}</span>
        {translateStatus(status)}
      </span>
    );
  };

  const filteredRequests = filter === 'all' 
    ? requests 
    : requests.filter(r => r.status === filter);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🔐 Cereri Acces Beta
          </h1>
          <p className="text-gray-600">
            Gestionați cererile de acces la platforma VitiScan
          </p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Cereri</div>
            <div className="text-3xl font-bold text-gray-900">{requests.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">În Așteptare</div>
            <div className="text-3xl font-bold text-yellow-600">
              {requests.filter(r => r.status === 'pending').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Aprobate</div>
            <div className="text-3xl font-bold text-green-600">
              {requests.filter(r => r.status === 'approved').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Respinse</div>
            <div className="text-3xl font-bold text-red-600">
              {requests.filter(r => r.status === 'rejected').length}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filtrer:</span>
            {(['all', 'pending', 'approved', 'rejected'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as 'all' | 'pending' | 'approved' | 'rejected')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === f
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {translateStatus(f)}
              </button>
            ))}
          </div>
        </div>

        {/* Requests Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilizator
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Societate / Regiune
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acțiuni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRequests.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      Nicio cerere găsită
                    </td>
                  </tr>
                ) : (
                  filteredRequests.map((request) => (
                    <tr key={request.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{request.full_name}</div>
                        {request.reason && (
                          <div className="text-xs text-gray-500 mt-1 max-w-xs truncate">
                            {request.reason}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{request.email}</div>
                        <div className="text-xs text-gray-500">{request.phone}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{request.company || '-'}</div>
                        <div className="text-xs text-gray-500">{request.region || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(request.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(request.created_at).toLocaleDateString('ro-RO', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {request.status === 'pending' && (
                          <div className="flex justify-end space-x-2">
                            <button
                              onClick={() => handleApprove(request.id)}
                              disabled={processing === request.id}
                              className="bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                              {processing === request.id ? '...' : 'Aprobă'}
                            </button>
                            <button
                              onClick={() => handleReject(request.id)}
                              disabled={processing === request.id}
                              className="bg-red-600 text-white px-3 py-1 rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                              {processing === request.id ? '...' : 'Respinge'}
                            </button>
                          </div>
                        )}
                        {request.status === 'approved' && request.register_token && (
                          <div className="text-xs text-gray-500">
                            Token trimis
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
