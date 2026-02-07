'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

interface AuthzRequest {
  subject: {
    id: string;
    role: string;
    attrs?: Record<string, any>;
  };
  resource: {
    id: string;
    type: string;
    attrs?: Record<string, any>;
    relations?: Record<string, any>;
  };
  action: string;
}

interface AuthzResponse {
  decision: 'allow' | 'deny';
  reasons: string[];
  matched_policies: string[];
  rbac?: any;
  rebac?: any;
  abac?: any;
  dry_run?: boolean;
}

export default function AuthzDebugPage() {
  const [request, setRequest] = useState<AuthzRequest>({
    subject: {
      id: 'user:123',
      role: 'user',
      attrs: { mfa: false, region: 'PACA' }
    },
    resource: {
      id: 'parcel:456',
      type: 'parcel',
      attrs: {},
      relations: { owner: 'user:123' }
    },
    action: 'view'
  });

  const [response, setResponse] = useState<AuthzResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDryRun, setIsDryRun] = useState(true);

  const handleTest = async () => {
    setLoading(true);
    setError('');
    setResponse(null);

    try {
      const res = await api.post(`/authz/why?dry_run=${isDryRun}`, request);
      setResponse(res.data);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Request failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const presetScenarios = [
    {
      name: '👤 Admin Full Access',
      data: {
        subject: { id: 'user:admin_1', role: 'admin', attrs: { mfa: true } },
        resource: { type: 'parcel', id: 'parcel:1', relations: { owner: 'user:user_1' } },
        action: 'delete'
      }
    },
    {
      name: '🔒 MFA Required (Delete)',
      data: {
        subject: { id: 'user:user_1', role: 'user', attrs: { mfa: false } },
        resource: { type: 'parcel', id: 'parcel:1', relations: { owner: 'user:user_1' } },
        action: 'delete'
      }
    },
    {
      name: '🌍 Region Restriction',
      data: {
        subject: { id: 'user:user_1', role: 'user', attrs: { region: 'Occitanie', mfa: true } },
        resource: { type: 'parcel', id: 'parcel:1', attrs: { region: 'PACA' }, relations: { owner: 'user:user_2' } },
        action: 'edit'
      }
    },
    {
      name: '👁️ Viewer (ReBAC)',
      data: {
        subject: { id: 'user:consultant_1', role: 'consultant', attrs: { mfa: true } },
        resource: { type: 'parcel', id: 'parcel:1', relations: { consultant: ['user:consultant_1'] } },
        action: 'view'
      }
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🧪 Authorization Debugger
          </h1>
          <p className="text-gray-600">
            Testează și simulează decizii de autorizare fără efecte (dry run)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel: Request Builder */}
          <div className="space-y-6">
            {/* Preset Scenarios */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                📋 Scenarii Predefinite
              </h2>
              <div className="space-y-2">
                {presetScenarios.map((scenario, index) => (
                  <button
                    key={index}
                    onClick={() => setRequest(scenario.data)}
                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-green-50 border border-gray-200 hover:border-green-300 rounded-lg transition-colors"
                  >
                    <div className="font-medium text-gray-900">{scenario.name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {scenario.data.subject.role} → {scenario.data.action} {scenario.data.resource.type}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Request JSON Editor */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                🛠️ Request Manual
              </h2>
              
              <div className="space-y-4">
                {/* Subject */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject (User):
                  </label>
                  <textarea
                    value={JSON.stringify(request.subject, null, 2)}
                    onChange={(e) => {
                      try {
                        const subject = JSON.parse(e.target.value);
                        setRequest({ ...request, subject });
                      } catch {}
                    }}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-xs focus:ring-2 focus:ring-green-500"
                  />
                </div>

                {/* Resource */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Resource:
                  </label>
                  <textarea
                    value={JSON.stringify(request.resource, null, 2)}
                    onChange={(e) => {
                      try {
                        const resource = JSON.parse(e.target.value);
                        setRequest({ ...request, resource });
                      } catch {}
                    }}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-xs focus:ring-2 focus:ring-green-500"
                  />
                </div>

                {/* Action */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Action:
                  </label>
                  <select
                    value={request.action}
                    onChange={(e) => setRequest({ ...request, action: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                      <option value="view">view</option>
                      <option value="edit">edit</option>
                      <option value="delete">delete</option>
                      <option value="manage">manage</option>
                  </select>
                </div>

                {/* Dry Run Toggle */}
                <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div>
                    <div className="font-medium text-blue-900">Dry Run Mode</div>
                    <div className="text-xs text-blue-700">
                      {isDryRun ? 'Nu va crea audit log' : 'Va crea audit log normal'}
                    </div>
                  </div>
                  <button
                    onClick={() => setIsDryRun(!isDryRun)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      isDryRun ? 'bg-green-600' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        isDryRun ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                {/* Test Button */}
                <button
                  onClick={handleTest}
                  disabled={loading}
                  className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Se testează...' : '🚀 Testează Autorizare'}
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel: Response */}
          <div className="space-y-6">
            {/* Response Display */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                📊 Rezultat
              </h2>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <span className="text-red-800 font-medium">Error:</span>
                  </div>
                  <p className="text-red-700 mt-2 text-sm">{error}</p>
                </div>
              )}

              {response && (
                <div className="space-y-4">
                  {/* Decision Badge */}
                  <div className="text-center py-6">
                    <div className={`inline-flex items-center px-6 py-3 rounded-full text-xl font-bold ${
                      response.decision === 'allow'
                        ? 'bg-green-100 text-green-800 border-2 border-green-300'
                        : 'bg-red-100 text-red-800 border-2 border-red-300'
                    }`}>
                      {response.decision === 'allow' ? '✅ ALLOW' : '🛑 DENY'}
                    </div>
                    {response.dry_run && (
                      <div className="mt-2 text-sm text-blue-600 font-medium">
                        (Dry Run - nu s-a salvat în audit log)
                      </div>
                    )}
                  </div>

                  {/* Matched Policies */}
                  {response.matched_policies && response.matched_policies.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="text-sm font-medium text-blue-900 mb-2">
                        Politici Aplicate:
                      </div>
                      <ul className="space-y-1">
                        {response.matched_policies.map((rule, index) => (
                          <li key={index} className="text-blue-800 text-sm">
                            • {rule}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Reasons */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-900 mb-2">
                      Motive:
                    </div>
                    {response.reasons && response.reasons.length > 0 ? (
                      <ul className="space-y-1 text-gray-700 text-sm">
                        {response.reasons.map((reason, index) => (
                          <li key={index}>• {reason}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-700 text-sm">Nicio explicație specifică.</p>
                    )}
                  </div>

                  {/* Full JSON */}
                  <details className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <summary className="cursor-pointer font-medium text-gray-900 text-sm">
                      Vezi JSON Complet
                    </summary>
                    <pre className="mt-3 text-xs overflow-auto">
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </details>
                </div>
              )}

              {!response && !error && !loading && (
                <div className="text-center py-12 text-gray-400">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <p>Configurează și testează o autorizare</p>
                </div>
              )}
            </div>

            {/* Usage Guide */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                💡 Cum Folosești
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>1️⃣ Selectează un scenariu predefinit SAU editează JSON manual</li>
                <li>2️⃣ Activează <strong>Dry Run</strong> pentru testare fără efecte</li>
                <li>3️⃣ Apasă <strong>Testează Autorizare</strong></li>
                <li>4️⃣ Vezi explicația detaliată a deciziei</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
