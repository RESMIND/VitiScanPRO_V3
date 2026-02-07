'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { establishmentsAPI } from '@/lib/api';

interface Tenant {
  tenant_id: string;
  establishment_id: string;
  establishment_name: string;
  role: string;
  joined_at: string;
}

interface TenantSelectorProps {
  onTenantChange?: (tenantId: string) => void;
}

export default function TenantSelector({ onTenantChange }: TenantSelectorProps) {
  const router = useRouter();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [currentTenant, setCurrentTenant] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTenants();
  }, []);

  const loadTenants = async () => {
    try {
      const data = await establishmentsAPI.getMine();
      const mapped: Tenant[] = (data || []).map((est: any) => ({
        tenant_id: `est:${est.id}`,
        establishment_id: est.id,
        establishment_name: est.name,
        role: est.role || 'owner',
        joined_at: est.created_at || new Date().toISOString(),
      }));
      setTenants(mapped);

      // Set current tenant from localStorage or first tenant
      const savedTenant = localStorage.getItem('current_tenant_id');
      if (savedTenant && mapped.some((t: Tenant) => t.tenant_id === savedTenant)) {
        setCurrentTenant(savedTenant);
      } else if (mapped.length > 0) {
        setCurrentTenant(mapped[0].tenant_id);
        localStorage.setItem('current_tenant_id', mapped[0].tenant_id);
      }
    } catch (error) {
      console.error('Error loading tenants:', error);
    } finally {
      setLoading(false);
    }
  };

  const switchTenant = async (tenantId: string) => {
    try {
      setCurrentTenant(tenantId);
      localStorage.setItem('current_tenant_id', tenantId);
      setIsOpen(false);

      if (onTenantChange) {
        onTenantChange(tenantId);
      }

      // Reload page to refresh data with new tenant context
      router.refresh();
    } catch (error) {
      console.error('Error switching tenant:', error);
    }
  };

  if (loading || tenants.length === 0) {
    return null;
  }

  const current = tenants.find(t => t.tenant_id === currentTenant);

  return (
    <div className="relative">
      {/* Current Tenant Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <span className="text-xl">🏛️</span>
        <div className="text-left min-w-0 flex-1">
          <div className="text-sm font-medium text-gray-900 truncate">
            {current?.establishment_name || 'Select Farm'}
          </div>
          {current && (
            <div className="text-xs text-gray-500">{current.role}</div>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu */}
          <div className="absolute right-0 mt-2 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
            <div className="p-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Fermele tale ({tenants.length})
              </div>
              
              {tenants.map((tenant) => (
                <button
                  key={tenant.tenant_id}
                  onClick={() => switchTenant(tenant.tenant_id)}
                  className={`w-full flex items-start space-x-3 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors ${
                    tenant.tenant_id === currentTenant ? 'bg-green-50' : ''
                  }`}
                >
                  <span className="text-2xl">🏛️</span>
                  <div className="flex-1 text-left min-w-0">
                    <div className="font-medium text-gray-900 truncate">
                      {tenant.establishment_name}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                        {tenant.role}
                      </span>
                      <span className="text-xs text-gray-500">
                        Din {new Date(tenant.joined_at).toLocaleDateString('ro-RO')}
                      </span>
                    </div>
                  </div>
                  {tenant.tenant_id === currentTenant && (
                    <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
            
            {/* Footer Actions */}
            <div className="border-t border-gray-200 p-2">
              <button
                onClick={() => {
                  setIsOpen(false);
                  router.push('/establishments');
                }}
                className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Adaugă fermă nouă</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
