'use client';

import { useEffect, useState } from 'react';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert, SuccessAlert } from '@/components/UIComponents';
import { authAPI } from '@/lib/api';

interface User {
  id: string;
  username?: string;
  role: string;
  language?: string;
  created_at: string;
}

export default function ProfileSettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  // Profile form
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    phone: ''
  });

  // Password form
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await authAPI.getProfile();
      setUser(data);
      setProfileForm({
        full_name: '',
        phone: ''
      });
    } catch (error) {
      console.error('Error loading profile:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea profilului';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      setError('Actualizarea profilului nu este disponibilă încă.');
    } catch (error: any) {
      setError(error.message || 'Eroare la actualizarea profilului');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('Parolele noi nu coincid');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setError('Parola nouă trebuie să aibă minimum 8 caractere');
      return;
    }

    setSaving(true);

    try {
      setError('Schimbarea parolei nu este disponibilă încă.');
    } catch (error: any) {
      setError(error.message || 'Eroare la schimbarea parolei');
    } finally {
      setSaving(false);
    }
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
      <div className="max-w-4xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Setări', href: '/settings/profile' },
          { label: 'Profil' }
        ]} />

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Setări Profil</h1>
          <p className="text-gray-600 mt-2">Gestionează informațiile personale și securitatea contului</p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess('')} />}

        {/* Profile Information */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Informații Personale</h2>
          
          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 mt-1">Username-ul nu poate fi modificat</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nume complet *
              </label>
              <input
                type="text"
                value={profileForm.full_name}
                onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Telefon
              </label>
              <input
                type="tel"
                value={profileForm.phone}
                onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                placeholder="+40 XXX XXX XXX"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-gray-500">
                Cont creat: {new Date(user?.created_at || '').toLocaleDateString('ro-RO')}
              </div>
              <button
                type="submit"
                disabled={saving}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors"
              >
                {saving ? 'Se salvează...' : 'Salvează modificările'}
              </button>
            </div>
          </form>
        </div>

        {/* Password Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Parolă</h2>
              <p className="text-sm text-gray-600 mt-1">Schimbă parola contului tău</p>
            </div>
            {!showPasswordForm && (
              <button
                onClick={() => setShowPasswordForm(true)}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
              >
                Schimbă parola
              </button>
            )}
          </div>

          {showPasswordForm && (
            <form onSubmit={handleChangePassword} className="space-y-4 mt-4 pt-4 border-t">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Parola curentă *
                </label>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Parola nouă * (minimum 8 caractere)
                </label>
                <input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                  minLength={8}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmă parola nouă *
                </label>
                <input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                  minLength={8}
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  {saving ? 'Se schimbă...' : 'Schimbă parola'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordForm(false);
                    setPasswordForm({
                      current_password: '',
                      new_password: '',
                      confirm_password: ''
                    });
                  }}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Anulează
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Account Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Status Cont</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-700">Rol</span>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                {user?.role}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-700">Limbă</span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                {user?.language || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
