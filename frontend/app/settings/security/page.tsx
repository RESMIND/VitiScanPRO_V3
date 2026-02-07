'use client';

import { useEffect, useState } from 'react';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert, SuccessAlert, EmptyState } from '@/components/UIComponents';
import { adminAPI } from '@/lib/api';

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  last_activity: string;
  is_current: boolean;
}

interface AuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
  metadata?: any;
}

export default function SecuritySettingsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showMfaInfo, setShowMfaInfo] = useState(false);

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      // Load active sessions (mock data for now)
      const currentSession: Session = {
        id: '1',
        ip_address: '192.168.1.1',
        user_agent: navigator.userAgent,
        created_at: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        is_current: true
      };
      setSessions([currentSession]);

      // Load recent audit logs
      const auditData = await adminAPI.getAuditLogs({ limit: 10 });
      const logs = (auditData?.logs || []).map((log: any) => ({
        id: log._id || log.id,
        action: log.action,
        resource_type: log.resource_type,
        resource_id: log.resource_id,
        ip_address: log.ip_address || 'N/A',
        user_agent: log.user_agent || 'N/A',
        created_at: log.timestamp || log.created_at,
        metadata: log.details || log.metadata,
      })) as AuditLog[];
      setAuditLogs(logs);
    } catch (error) {
      console.error('Error loading security data:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea datelor de securitate';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleTerminateSession = async (sessionId: string) => {
    if (!confirm('Sigur vrei să termini această sesiune?')) {
      return;
    }

    try {
      setSuccess('Sesiune terminată cu succes!');
      await loadSecurityData();
    } catch (error: any) {
      setError(error.message || 'Eroare la terminarea sesiunii');
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('login')) return '🔐';
    if (action.includes('create')) return '✅';
    if (action.includes('update')) return '✏️';
    if (action.includes('delete')) return '🗑️';
    if (action.includes('share')) return '🔗';
    return '📝';
  };

  const getActionColor = (action: string) => {
    if (action.includes('login')) return 'text-blue-600';
    if (action.includes('create')) return 'text-green-600';
    if (action.includes('update')) return 'text-yellow-600';
    if (action.includes('delete')) return 'text-red-600';
    if (action.includes('share')) return 'text-purple-600';
    return 'text-gray-600';
  };

  const getBrowserName = (userAgent: string) => {
    if (userAgent.includes('Firefox')) return 'Firefox';
    if (userAgent.includes('Chrome')) return 'Chrome';
    if (userAgent.includes('Safari')) return 'Safari';
    if (userAgent.includes('Edge')) return 'Edge';
    return 'Unknown Browser';
  };

  const getDeviceType = (userAgent: string) => {
    if (userAgent.includes('Mobile')) return '📱 Mobile';
    if (userAgent.includes('Tablet')) return '📱 Tablet';
    return '💻 Desktop';
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
      <div className="max-w-6xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Setări', href: '/settings/profile' },
          { label: 'Securitate' }
        ]} />

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Setări Securitate</h1>
          <p className="text-gray-600 mt-2">Gestionează securitatea și confidențialitatea contului tău</p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess('')} />}

        {/* MFA Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🔒</div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Autentificare în Doi Pași (MFA)</h2>
                <p className="text-sm text-gray-600 mt-1">Protejează-ți contul cu un nivel suplimentar de securitate</p>
              </div>
            </div>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              🚧 În curând
            </span>
          </div>

          {showMfaInfo && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Ce este MFA?</h3>
              <p className="text-sm text-blue-800 mb-3">
                Autentificarea în doi pași (Multi-Factor Authentication) adaugă un nivel suplimentar de securitate la contul tău. 
                După introducerea parolei, va trebui să introduci și un cod primit prin SMS sau generat de o aplicație de autentificare.
              </p>
              <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                <li>Protecție împotriva accesului neautorizat</li>
                <li>Cod generat prin SMS sau aplicație (Google Authenticator, Authy)</li>
                <li>Recomandată pentru toți utilizatorii</li>
              </ul>
            </div>
          )}

          <button
            onClick={() => setShowMfaInfo(!showMfaInfo)}
            className="mt-4 text-green-600 hover:text-green-700 text-sm font-medium"
          >
            {showMfaInfo ? 'Ascunde detalii' : 'Află mai multe →'}
          </button>
        </div>

        {/* Active Sessions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sesiuni Active</h2>
          
          {sessions.length === 0 ? (
            <EmptyState
              icon="🔐"
              title="Nu există sesiuni active"
              description="Nu s-au găsit sesiuni active pentru contul tău"
            />
          ) : (
            <div className="space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`p-4 border rounded-lg ${
                    session.is_current
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-xl">{getDeviceType(session.user_agent)}</span>
                        <span className="font-medium text-gray-900">
                          {getBrowserName(session.user_agent)}
                        </span>
                        {session.is_current && (
                          <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            Sesiune curentă
                          </span>
                        )}
                      </div>
                      
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <span>🌐 IP:</span>
                          <span>{session.ip_address}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span>📅 Început:</span>
                          <span>{new Date(session.created_at).toLocaleString('ro-RO')}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span>⏰ Ultima activitate:</span>
                          <span>{new Date(session.last_activity).toLocaleString('ro-RO')}</span>
                        </div>
                      </div>
                    </div>

                    {!session.is_current && (
                      <button
                        onClick={() => handleTerminateSession(session.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Termină sesiune
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity (Audit Logs) */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Activitate Recentă</h2>
            <a
              href="/admin/audit/logs"
              className="text-green-600 hover:text-green-700 text-sm font-medium"
            >
              Vezi toate →
            </a>
          </div>

          {auditLogs.length === 0 ? (
            <EmptyState
              icon="📊"
              title="Nu există activitate"
              description="Nu s-au înregistrat acțiuni recente pe contul tău"
            />
          ) : (
            <div className="space-y-3">
              {auditLogs.map((log) => (
                <div
                  key={log.id}
                  className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`text-2xl ${getActionColor(log.action)}`}>
                    {getActionIcon(log.action)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">{log.action}</span>
                      {log.resource_type && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                          {log.resource_type}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                      <span>🌐 {log.ip_address}</span>
                      <span>📅 {new Date(log.created_at).toLocaleString('ro-RO')}</span>
                    </div>

                    {log.metadata && Object.keys(log.metadata).length > 0 && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-xs text-gray-600 hover:text-gray-900">
                          Detalii
                        </summary>
                        <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Security Recommendations */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-6">
          <div className="flex items-start space-x-3">
            <div className="text-3xl">💡</div>
            <div>
              <h3 className="font-semibold text-yellow-900 mb-2">Recomandări de Securitate</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-yellow-800">
                <li>Folosește o parolă puternică (minim 8 caractere, litere mari/mici, cifre, simboluri)</li>
                <li>Schimbă parola periodic (recomandat: la fiecare 3 luni)</li>
                <li>Nu partaja parola cu alte persoane</li>
                <li>Verifică sesiunile active regulat și termină sesiunile suspecte</li>
                <li>Activează autentificarea în doi pași când va fi disponibilă</li>
                <li>Verifică activitatea recentă pentru orice acțiuni neautorizate</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
