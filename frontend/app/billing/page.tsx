'use client';

import { useEffect, useState } from 'react';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert, SuccessAlert } from '@/components/UIComponents';
import { billingAPI } from '@/lib/api';

interface UsageStats {
  plan: string;
  usage: {
    parcels: { current: number; limit: number; unlimited: boolean };
    scans_this_month: { current: number; limit: number; unlimited: boolean };
    team_members: { current: number; limit: number; unlimited: boolean };
    storage_mb: { current: number; limit: number; unlimited: boolean };
  };
}

interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
  limits: {
    parcels: number;
    scans_per_month: number;
    storage_mb: number;
    team_members: number;
  };
  recommended?: boolean;
}

export default function BillingPage() {
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const plans: Plan[] = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      currency: 'EUR',
      interval: 'lună',
      features: [
        'Până la 3 parcele',
        '10 scanări / lună',
        '100 MB stocare',
        '1 membru în echipă',
        'Suport comunitate'
      ],
      limits: {
        parcels: 3,
        scans_per_month: 10,
        storage_mb: 100,
        team_members: 1
      }
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 10,
      currency: 'EUR',
      interval: 'lună',
      features: [
        'Până la 50 parcele',
        '500 scanări / lună',
        '5 GB stocare',
        '10 membri în echipă',
        'Suport prioritar',
        'Export date CSV/Excel',
        'API access'
      ],
      limits: {
        parcels: 50,
        scans_per_month: 500,
        storage_mb: 5000,
        team_members: 10
      },
      recommended: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 99,
      currency: 'EUR',
      interval: 'lună',
      features: [
        'Parcele nelimitate',
        'Scanări nelimitate',
        'Stocare nelimitată',
        'Membri nelimitați',
        'Suport dedicat 24/7',
        'SLA garantat',
        'On-premise deployment',
        'Custom integrations'
      ],
      limits: {
        parcels: -1,
        scans_per_month: -1,
        storage_mb: -1,
        team_members: -1
      }
    }
  ];

  useEffect(() => {
    loadUsageStats();
  }, []);

  const loadUsageStats = async () => {
    try {
      const data = await billingAPI.getUsage();
      setUsage(data);
    } catch (error) {
      console.error('Error loading usage stats:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea statisticilor';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planId: string) => {
    setError('');
    setSuccess('');

    try {
      const data = await billingAPI.createCheckout(planId);
      // Redirect to Stripe Checkout (if configured)
      if (data?.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Eroare la procesarea plății';
      setError(message);
    }
  };

  const getProgressColor = (current: number, limit: number) => {
    if (limit === -1) return 'bg-green-600';
    const percentage = (current / limit) * 100;
    if (percentage >= 90) return 'bg-red-600';
    if (percentage >= 70) return 'bg-yellow-600';
    return 'bg-green-600';
  };

  const getProgressPercentage = (current: number, limit: number) => {
    if (limit === -1) return 0;
    return Math.min((current / limit) * 100, 100);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <LoadingSpinner />
      </div>
    );
  }

  const currentPlan = usage?.plan || 'free';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Setări', href: '/settings/profile' },
          { label: 'Billing & Abonament' }
        ]} />

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Billing & Abonament</h1>
          <p className="text-gray-600 mt-2">Gestionează planul de abonament și utilizarea</p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess('')} />}

        {/* Current Usage */}
        {usage && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Utilizare Curentă</h2>
              <span className="px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                Plan: {currentPlan.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Parcels */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Parcele</span>
                  <span className="text-sm text-gray-600">
                    {usage.usage.parcels.current} / {usage.usage.parcels.unlimited ? '∞' : usage.usage.parcels.limit}
                  </span>
                </div>
                {!usage.usage.parcels.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(usage.usage.parcels.current, usage.usage.parcels.limit)}`}
                      style={{ width: `${getProgressPercentage(usage.usage.parcels.current, usage.usage.parcels.limit)}%` }}
                    />
                  </div>
                )}
              </div>

              {/* Scans */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Scanări luna aceasta</span>
                  <span className="text-sm text-gray-600">
                    {usage.usage.scans_this_month.current} / {usage.usage.scans_this_month.unlimited ? '∞' : usage.usage.scans_this_month.limit}
                  </span>
                </div>
                {!usage.usage.scans_this_month.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(usage.usage.scans_this_month.current, usage.usage.scans_this_month.limit)}`}
                      style={{ width: `${getProgressPercentage(usage.usage.scans_this_month.current, usage.usage.scans_this_month.limit)}%` }}
                    />
                  </div>
                )}
              </div>

              {/* Team Members */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Membri echipă</span>
                  <span className="text-sm text-gray-600">
                    {usage.usage.team_members.current} / {usage.usage.team_members.unlimited ? '∞' : usage.usage.team_members.limit}
                  </span>
                </div>
                {!usage.usage.team_members.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(usage.usage.team_members.current, usage.usage.team_members.limit)}`}
                      style={{ width: `${getProgressPercentage(usage.usage.team_members.current, usage.usage.team_members.limit)}%` }}
                    />
                  </div>
                )}
              </div>

              {/* Storage */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Stocare</span>
                  <span className="text-sm text-gray-600">
                    {usage.usage.storage_mb.current} MB / {usage.usage.storage_mb.unlimited ? '∞' : usage.usage.storage_mb.limit} MB
                  </span>
                </div>
                {!usage.usage.storage_mb.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(usage.usage.storage_mb.current, usage.usage.storage_mb.limit)}`}
                      style={{ width: `${getProgressPercentage(usage.usage.storage_mb.current, usage.usage.storage_mb.limit)}%` }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Plans */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Alege planul potrivit</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`bg-white rounded-lg shadow-md p-6 ${
                  plan.recommended ? 'border-2 border-green-500 relative' : 'border border-gray-200'
                }`}
              >
                {plan.recommended && (
                  <div className="absolute top-0 right-0 bg-green-500 text-white px-4 py-1 text-xs font-semibold rounded-bl-lg rounded-tr-lg">
                    RECOMANDAT
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}€</span>
                    <span className="text-gray-600 ml-2">/ {plan.interval}</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.id === currentPlan ? (
                  <button
                    disabled
                    className="w-full bg-gray-100 text-gray-500 px-6 py-3 rounded-lg font-medium cursor-not-allowed"
                  >
                    Plan curent
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade(plan.id)}
                    className={`w-full px-6 py-3 rounded-lg font-medium transition-colors ${
                      plan.recommended
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                    }`}
                  >
                    {plan.price === 0 ? 'Downgrade' : 'Upgrade'}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Stripe Integration Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <div className="text-2xl">ℹ️</div>
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Plăți sigure cu Stripe</h3>
              <p className="text-sm text-blue-800 mb-3">
                Toate plățile sunt procesate securizat prin Stripe. Nu stocăm informații despre carduri.
                Poți anula abonamentul oricând.
              </p>
              <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                <li>Plăți securizate PCI-compliant</li>
                <li>Factură automată lunară</li>
                <li>Anulare oricând, fără penalități</li>
                <li>Suport dedicat pentru probleme de facturare</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
