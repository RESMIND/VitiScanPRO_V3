'use client';

import { useState, useEffect } from 'react';
import { ErrorAlert } from '@/components/UIComponents';
import { adminAPI } from '@/lib/api';

interface AuditLog {
  timestamp: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  outcome: 'allow' | 'deny';
  mechanism?: string;
  details?: any;
}

interface AuditStats {
  total_checks: number;
  allowed: number;
  denied: number;
  allow_rate: number;
  most_active_users: Array<{ user_id: string; checks: number }>;
  most_accessed_resources: Array<{ resource: string; accesses: number }>;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    outcome: '',
    days: 7
  });
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [filters]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      setError('');
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - filters.days);

      const data = await adminAPI.getAuditLogs({
        limit: 200,
        user_id: filters.user_id || undefined,
        action: filters.action || undefined,
        outcome: filters.outcome || undefined,
        start_date: startDate.toISOString(),
      });

      setLogs(data?.logs || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea logurilor';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await adminAPI.getAuditStats(filters.days);
      setStats(data || null);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea statisticilor';
      setError(message);
    }
  };

  const getOutcomeBadge = (outcome: string) => {
    return outcome === 'allow' ? (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        ✅ ALLOW
      </span>
    ) : (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        🛑 DENY
      </span>
    );
  };

  const getMechanismBadge = (mechanism?: string) => {
    if (!mechanism) return null;
    
    const colors: Record<string, string> = {
      rbac: 'bg-blue-100 text-blue-800',
      abac: 'bg-purple-100 text-purple-800',
      rebac: 'bg-orange-100 text-orange-800'
    };

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[mechanism] || 'bg-gray-100 text-gray-800'}`}>
        {mechanism.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📊 Jurnal Audit
          </h1>
          <p className="text-gray-600">
            Istoric complet al deciziilor de autorizare
          </p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Evenimente</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_checks}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Acces Permis</div>
              <div className="text-3xl font-bold text-green-600">{stats.allowed}</div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.total_checks > 0 ? Math.round((stats.allowed / stats.total_checks) * 100) : 0}% din total
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Acces Refuzat</div>
              <div className="text-3xl font-bold text-red-600">{stats.denied}</div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.total_checks > 0 ? Math.round((stats.denied / stats.total_checks) * 100) : 0}% din total
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Top Utilizator</div>
              <div className="text-lg font-bold text-gray-900 truncate">
                {stats.most_active_users[0]?.user_id || 'N/A'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.most_active_users[0]?.checks || 0} evenimente
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ID Utilizator
              </label>
              <input
                type="text"
                value={filters.user_id}
                onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="user_123"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Acțiune
              </label>
              <select
                value={filters.action}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              >
                <option value="">Toate</option>
                <option value="read">Citire</option>
                <option value="write">Scriere</option>
                <option value="delete">Ștergere</option>
                <option value="share">Partajare</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rezultat
              </label>
              <select
                value={filters.outcome}
                onChange={(e) => setFilters({ ...filters, outcome: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              >
                <option value="">Toate</option>
                <option value="allow">Permis</option>
                <option value="deny">Refuzat</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Perioadă
              </label>
              <select
                value={filters.days}
                onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              >
                <option value={1}>Azi</option>
                <option value={7}>Ultimele 7 zile</option>
                <option value={30}>Ultimele 30 zile</option>
                <option value={90}>Ultimele 90 zile</option>
              </select>
            </div>
          </div>
        </div>

        {/* Logs Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilizator
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acțiune
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Resursă
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mecanism
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rezultat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Detalii
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                      Niciun log găsit
                    </td>
                  </tr>
                ) : (
                  logs.map((log, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(log.timestamp).toLocaleString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {log.user_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.action}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="font-mono text-xs">
                          {log.resource_type}:{log.resource_id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getMechanismBadge(log.mechanism)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getOutcomeBadge(log.outcome)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="text-green-600 hover:text-green-800 text-sm font-medium"
                        >
                          Detalii 🔍
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Details Modal */}
        {selectedLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-gray-900">
                    Detalii Eveniment
                  </h3>
                  <button
                    onClick={() => setSelectedLog(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Timestamp:</span>
                    <div className="text-gray-900">{new Date(selectedLog.timestamp).toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">ID Utilizator:</span>
                    <div className="text-gray-900">{selectedLog.user_id}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Acțiune:</span>
                    <div className="text-gray-900">{selectedLog.action}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Resursă:</span>
                    <div className="text-gray-900 font-mono text-sm">
                      {selectedLog.resource_type}:{selectedLog.resource_id}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Mecanism:</span>
                    <div>{getMechanismBadge(selectedLog.mechanism)}</div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Rezultat:</span>
                    <div>{getOutcomeBadge(selectedLog.outcome)}</div>
                  </div>
                  {selectedLog.details && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Detalii Complete:</span>
                      <pre className="mt-2 bg-gray-50 p-4 rounded-lg text-xs overflow-auto">
                        {JSON.stringify(selectedLog.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
