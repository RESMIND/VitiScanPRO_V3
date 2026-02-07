'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { betaRequestsAPI } from '@/lib/api';

export default function BetaRequestPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    full_name: '',
    company: '',
    region: '',
    reason: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await betaRequestsAPI.create({
        email: formData.email,
        phone: formData.phone,
        name: formData.full_name,
        farm_name: formData.company || 'N/A',
        region: formData.region || undefined,
        reason: formData.reason || undefined,
      });

      setSuccess(true);
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'La demande n\'a pas pu être envoyée';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Demande Envoyée !</h2>
          <p className="text-gray-600 mb-4">
            Nous avons reçu votre demande d'accès beta. Vous recevrez un SMS et un email avec les instructions sous peu.
          </p>
          <p className="text-sm text-gray-500">Redirection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🌱 Accès Beta VitiScan
          </h1>
          <p className="text-gray-600">
            Demandez l'accès à la plateforme de gestion agricole pour viticulteurs
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Adresse Email *
            </label>
            <input
              type="email"
              id="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="votre@email.com"
            />
          </div>

          {/* Phone */}
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              Numéro de Téléphone *
            </label>
            <input
              type="tel"
              id="phone"
              required
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="+33 6 XX XX XX XX"
            />
          </div>

          {/* Full Name */}
          <div>
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
              Nom Complet *
            </label>
            <input
              type="text"
              id="full_name"
              required
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Jean Dupont"
            />
          </div>

          {/* Company */}
          <div>
            <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
              Société / Domaine
            </label>
            <input
              type="text"
              id="company"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Domaine Viticole SARL"
            />
          </div>

          {/* Region */}
          <div>
            <label htmlFor="region" className="block text-sm font-medium text-gray-700 mb-2">
              Région
            </label>
            <select
              id="region"
              value={formData.region}
              onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Sélectionnez votre région</option>
              <option value="PACA">Provence-Alpes-Côte d'Azur</option>
              <option value="Occitanie">Occitanie</option>
              <option value="Nouvelle-Aquitaine">Nouvelle-Aquitaine</option>
              <option value="Bourgogne">Bourgogne-Franche-Comté</option>
              <option value="Champagne">Grand Est (Champagne)</option>
              <option value="Vallée du Rhône">Auvergne-Rhône-Alpes</option>
            </select>
          </div>

          {/* Reason */}
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-2">
              Pourquoi voulez-vous accéder à la beta ?
            </label>
            <textarea
              id="reason"
              rows={4}
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Décrivez comment vous utiliseriez VitiScan dans votre activité..."
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Envoi en cours...' : 'Envoyer la Demande'}
          </button>

          <p className="text-xs text-gray-500 text-center">
            Vous recevrez un SMS et un email avec les instructions pour finaliser votre compte.
          </p>
        </form>
      </div>
    </div>
  );
}
