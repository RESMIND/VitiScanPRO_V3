'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  name: string;
  href: string;
  icon: string;
  badge?: number;
  adminOnly?: boolean;
}

interface SidebarProps {
  isAdmin?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isAdmin = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Exploatații', href: '/establishments', icon: '🏛️' },
    { name: 'Parcelele Mele', href: '/parcels', icon: '🌱' },
    { name: 'Scanări', href: '/scans', icon: '📸' },
    ...(isAdmin ? [
      { name: 'Beta Requests', href: '/admin/beta-requests', icon: '🔐', adminOnly: true },
      { name: 'Audit Logs', href: '/admin/audit/logs', icon: '📊', adminOnly: true },
      { name: 'Authz Debug', href: '/authz/debug', icon: '🧪', adminOnly: true }
    ] : []),
    { name: 'Setări', href: '/settings/profile', icon: '⚙️' }
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/' || pathname === '/dashboard';
    }
    return pathname?.startsWith(href);
  };

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <span className="text-2xl">🌱</span>
          <span className="text-xl font-bold text-green-600">VitiScan</span>
        </Link>
        {onClose && (
          <button onClick={onClose} className="md:hidden text-gray-600 hover:text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            onClick={onClose}
            className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
              isActive(item.href)
                ? 'bg-green-50 text-green-700'
                : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <span className="text-xl mr-3">{item.icon}</span>
            <span className="flex-1">{item.name}</span>
            {item.adminOnly && (
              <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded-full">
                Admin
              </span>
            )}
            {item.badge !== undefined && item.badge > 0 && (
              <span className="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded-full">
                {item.badge}
              </span>
            )}
          </Link>
        ))}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <span className="text-green-600 font-semibold">👤</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {typeof localStorage !== 'undefined' && localStorage.getItem('user_email') || 'Utilizator'}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {isAdmin ? 'Administrator' : 'Utilizator'}
            </p>
          </div>
          <button
            onClick={() => {
              localStorage.clear();
              window.location.href = '/login';
            }}
            className="text-gray-400 hover:text-gray-600"
            title="Logout"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
