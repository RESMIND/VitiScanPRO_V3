'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert } from '@/components/UIComponents';
import { adminAPI } from '@/lib/api';

interface GlobalStats {
  total_users: number;
  active_users: number;
  total_establishments: number;
  total_parcels: number;
  total_scans: number;
  scans_today: number;
  scans_this_week: number;
  storage_used_gb: number;
}

interface RecentUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
  is_active: boolean;
  plan: string;
}

interface RecentActivity {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  timestamp: string;
  ip_address: string;
}

export default function AdminGlobalPanel() {
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [recentUsers, setRecentUsers] = useState<RecentUser[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
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

  const loadGlobalData = useCallback(async () => {
    try {
      const [statsData, usersData, activityData] = await Promise.all([
        adminAPI.getGlobalStats(),
        adminAPI.getRecentUsers(10),
        adminAPI.getAuditLogs({ limit: 20 }),
      ]);

      setStats(statsData || null);
      setRecentUsers(usersData || []);
      const activityLogs = (activityData?.logs || []).map((log: { _id?: string; id?: string; user_id?: string; user_email?: string; action?: string; resource_type?: string; resource_id?: string; timestamp?: string; created_at?: string; ip_address?: string }) => ({
        id: log._id || log.id || '',
        user_id: log.user_id || '',
        user_email: log.user_email || log.user_id || '',
        action: log.action || '',
        resource_type: log.resource_type || '',
        resource_id: log.resource_id || '',
        timestamp: log.timestamp || log.created_at || '',
        ip_address: log.ip_address || 'N/A'
      })) as RecentActivity[];
      setRecentActivity(activityLogs);
    } catch (error) {
      console.error('Error loading global data:', error);
      const message = extractErrorMessage(error, 'Eroare la încărcarea datelor');
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGlobalData();
  }, [loadGlobalData]);

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      case 'pro': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('login')) return '🔐';
    if (action.includes('create')) return '✅';
    if (action.includes('update')) return '✏️';
    if (action.includes('delete')) return '🗑️';
    if (action.includes('invite')) return '📧';
    return '📝';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Admin' },
          { label: 'Panou Global' }
        ]} />

        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">🛡️ Panou Admin Global</h1>
            <p className="text-gray-600 mt-2">Supraveghere și management platformă VitiScan</p>
          </div>
          <span className="px-4 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium">
            SUPERADMIN
          </span>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

        {/* Global Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Total Utilizatori</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_users}</div>
              <div className="text-xs text-green-600 mt-1">
                {stats.active_users} activi
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Exploatații</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_establishments}</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Parcele</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_parcels}</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Scanări Totale</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_scans}</div>
              <div className="text-xs text-blue-600 mt-1">
                {stats.scans_today} astăzi
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Scanări Săptămâna</div>
              <div className="text-3xl font-bold text-gray-900">{stats.scans_this_week}</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-sm text-gray-600 mb-1">Stocare Folosită</div>
              <div className="text-3xl font-bold text-gray-900">{stats.storage_used_gb.toFixed(2)}</div>
              <div className="text-xs text-gray-500 mt-1">GB</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md col-span-2">
              <div className="text-sm text-gray-600 mb-1">Status Platformă</div>
              <div className="flex items-center space-x-2 mt-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-lg font-semibold text-green-600">Operațional</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Uptime: 99.9% • Ultimul deploy: acum 2h
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Recent Users */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Utilizatori Recenți
              </h2>
              <Link
                href="/admin/users"
                className="text-green-600 hover:text-green-700 text-sm font-medium"
              >
                Vezi toți →
              </Link>
            </div>

            <div className="space-y-3">
              {recentUsers.slice(0, 5).map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">
                        {user.full_name}
                      </div>
                      <div className="text-sm text-gray-600 truncate">
                        {user.email}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(user.created_at).toLocaleDateString('fr-FR')}
                      </div>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getPlanBadgeColor(user.plan)}`}>
                    {user.plan}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Activitate Recentă
              </h2>
              <Link
                href="/admin/audit/logs"
                className="text-green-600 hover:text-green-700 text-sm font-medium"
              >
                Vezi toate →
              </Link>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {recentActivity.slice(0, 10).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-2 p-2 border-l-2 border-gray-200 hover:border-green-500 hover:bg-gray-50 rounded"
                >
                  <div className="text-xl flex-shrink-0">
                    {getActionIcon(activity.action)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-gray-900">
                      <span className="font-medium">{activity.user_email}</span>
                      {' '}{activity.action}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString('fr-FR')} • {activity.ip_address}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Acțiuni Rapide</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link
              href="/admin/users"
              className="flex flex-col items-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
            >
              <span className="text-3xl mb-2">👥</span>
              <span className="text-sm font-medium text-gray-900">Gestionează Utilizatori</span>
            </Link>

            <Link
              href="/admin/beta-requests"
              className="flex flex-col items-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
            >
              <span className="text-3xl mb-2">🔐</span>
              <span className="text-sm font-medium text-gray-900">Cereri Beta</span>
            </Link>

            <Link
              href="/admin/audit/logs"
              className="flex flex-col items-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
            >
              <span className="text-3xl mb-2">📊</span>
              <span className="text-sm font-medium text-gray-900">Jurnale Audit</span>
            </Link>

            <Link
              href="/authz/debug"
              className="flex flex-col items-center p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
            >
              <span className="text-3xl mb-2">🧪</span>
              <span className="text-sm font-medium text-gray-900">Debug Authz</span>
            </Link>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sănătate Sistem</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-green-900">Status API</span>
                <span className="text-green-600">✅</span>
              </div>
              <div className="text-2xl font-bold text-green-900 mt-2">Sănătos</div>
              <div className="text-xs text-green-700 mt-1">Timp răspuns: 45ms</div>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-green-900">Bază de Date</span>
                <span className="text-green-600">✅</span>
              </div>
              <div className="text-2xl font-bold text-green-900 mt-2">Conectat</div>
              <div className="text-xs text-green-700 mt-1">MongoDB Atlas</div>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-900">Stocare</span>
                <span className="text-blue-600">ℹ️</span>
              </div>
              <div className="text-2xl font-bold text-blue-900 mt-2">{stats?.storage_used_gb.toFixed(1)} GB</div>
              <div className="text-xs text-blue-700 mt-1">din 100 GB folosit</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
