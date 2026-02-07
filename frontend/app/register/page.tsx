'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    accept_terms: false,
    accept_privacy: false,
    marketing_consent: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Parolele nu se potrivesc');
      return;
    }

    if (formData.password.length < 6) {
      setError('Parola trebuie să aibă minim 6 caractere');
      return;
    }

    if (!formData.accept_terms || !formData.accept_privacy) {
      setError('Trebuie să accepți Termenii și Politica de confidențialitate');
      return;
    }

    setLoading(true);

    try {
      await authAPI.register({
        username: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        language: 'ro',
        role: 'user',
        accept_terms: formData.accept_terms,
        accept_privacy: formData.accept_privacy,
        marketing_consent: formData.marketing_consent,
      });
      // Auto-login după înregistrare
      await authAPI.login(formData.email, formData.password);
      router.push('/dashboard');
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((d: any) => d?.msg || d?.message || JSON.stringify(d)).join('; ')
        : typeof detail === 'string'
          ? detail
          : err?.message || 'Eroare la înregistrare';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-green-800">VitiScan v3</h1>
          <p className="text-gray-600 mt-2">Creare cont nou</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
              Nume complet
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Ion Popescu"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="adresa@email.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Parolă
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirmă parola
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="space-y-3">
            <label className="flex items-start gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                name="accept_terms"
                checked={formData.accept_terms}
                onChange={handleChange}
                className="mt-1"
                required
              />
              Accept Termenii și Condițiile
            </label>
            <label className="flex items-start gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                name="accept_privacy"
                checked={formData.accept_privacy}
                onChange={handleChange}
                className="mt-1"
                required
              />
              Accept Politica de confidențialitate
            </label>
            <label className="flex items-start gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                name="marketing_consent"
                checked={formData.marketing_consent}
                onChange={handleChange}
                className="mt-1"
              />
              Accept comunicări de marketing (opțional)
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-3 rounded-lg font-semibold transition-colors"
          >
            {loading ? 'Se creează contul...' : 'Înregistrare'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Ai deja cont?{' '}
            <Link href="/login" className="text-green-600 hover:text-green-700 font-semibold">
              Autentifică-te
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
