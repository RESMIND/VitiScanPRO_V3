'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { betaRequestsAPI } from '@/lib/api';

function RegisterCompletePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams?.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
    verificationCode: ''
  });
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [error, setError] = useState('');
  const [tokenData, setTokenData] = useState<any>(null);
  const [step, setStep] = useState<'password' | 'verify'>('password');
  const [phoneNumber, setPhoneNumber] = useState<string>('');

  useEffect(() => {
    if (!token) {
      setError('Token manquant. Lien invalide.');
      setVerifying(false);
      return;
    }

    // Verify token validity
    const verifyToken = async () => {
      try {
        const data = await betaRequestsAPI.verifyToken(token);
        setTokenData(data);
      } catch (err: any) {
        const message = err?.response?.data?.detail || err?.message || 'Token invalide ou expiré';
        setError(message);
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (step === 'password') {
      if (formData.password !== formData.confirmPassword) {
        setError('Les mots de passe ne correspondent pas');
        return;
      }

      if (formData.password.length < 8) {
        setError('Le mot de passe doit contenir au minimum 8 caractères');
        return;
      }

      setLoading(true);
      setError('');

      try {
        const response = await betaRequestsAPI.completeRegistration(token as string, formData.password);
        
        if (response.requires_verification) {
          setPhoneNumber(response.phone);
          setStep('verify');
          setError('');
        } else {
          // Registration completed without verification
          router.push('/login?registered=true');
        }
      } catch (err: any) {
        const message = err?.response?.data?.detail || err?.message || 'L\'enregistrement a échoué';
        setError(message);
      } finally {
        setLoading(false);
      }
    } else if (step === 'verify') {
      if (!formData.verificationCode || formData.verificationCode.length !== 6) {
        setError('Le code de vérification doit contenir 6 chiffres');
        return;
      }

      setLoading(true);
      setError('');

      try {
        await betaRequestsAPI.completeRegistrationWithVerification(token as string, formData.password, formData.verificationCode);
        router.push('/login?registered=true');
      } catch (err: any) {
        const message = err?.response?.data?.detail || err?.message || 'Code invalide ou expiré';
        setError(message);
      } finally {
        setLoading(false);
      }
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Vérification du token...</p>
        </div>
      </div>
    );
  }

  if (error && !tokenData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Token Invalide</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/beta-request')}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
          >
            Demander Accès Beta
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {step === 'password' ? 'Finaliser le Compte' : 'Vérification Téléphone'}
          </h1>
          <p className="text-gray-600">
            {step === 'password' 
              ? `Bienvenue, ${tokenData?.full_name}!`
              : 'Nous avons envoyé un code de vérification par SMS'
            }
          </p>
          {step === 'verify' && phoneNumber && (
            <p className="text-sm text-gray-500 mt-1">
              Numéro: {phoneNumber}
            </p>
          )}
          {step === 'password' && (
            <p className="text-sm text-gray-500 mt-1">
              {tokenData?.email}
            </p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {step === 'password' ? (
            <>
              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Mot de Passe *
                </label>
                <input
                  type="password"
                  id="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Minimum 8 caractères"
                />
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmer le Mot de Passe *
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Répétez le mot de passe"
                />
              </div>

              {/* Password Requirements */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">Exigences du mot de passe:</p>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li className={formData.password.length >= 8 ? 'text-green-600' : ''}>
                    ✓ Minimum 8 caractères
                  </li>
                  <li className={formData.password === formData.confirmPassword && formData.password ? 'text-green-600' : ''}>
                    ✓ Les mots de passe correspondent
                  </li>
                </ul>
              </div>
            </>
          ) : (
            <>
              {/* Verification Code */}
              <div>
                <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Code de Vérification SMS *
                </label>
                <input
                  type="text"
                  id="verificationCode"
                  required
                  maxLength={6}
                  value={formData.verificationCode}
                  onChange={(e) => setFormData({ ...formData, verificationCode: e.target.value.replace(/\D/g, '') })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-center text-2xl font-mono tracking-widest"
                  placeholder="000000"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Saisissez le code de 6 chiffres reçu par SMS
                </p>
              </div>

              {/* SMS Info */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-medium text-green-900 mb-2">📱 Code SMS envoyé</p>
                <p className="text-xs text-green-800">
                  Vérifiez vos messages SMS sur votre téléphone. Le code est valide 10 minutes.
                </p>
              </div>
            </>
          )}

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
            {loading 
              ? (step === 'password' ? 'Envoi du SMS...' : 'Vérification du code...') 
              : (step === 'password' ? 'Envoyer le Code SMS' : 'Créer le Compte')
            }
          </button>

          {step === 'verify' && (
            <button
              type="button"
              onClick={() => setStep('password')}
              className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors text-sm"
            >
              ← Retour au mot de passe
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

export default function RegisterCompletePageWrapper() {
  return (
    <Suspense fallback={<div>Chargement...</div>}>
      <RegisterCompletePage />
    </Suspense>
  );
}
