'use client';

import Link from 'next/link';

interface NavItem {
  href: string;
  label: string;
  badge?: string;
  icon?: string;
}

const adminNavItems: NavItem[] = [
  { href: '/admin/beta-requests', label: 'Beta Requests', icon: '🔐', badge: 'Admin' },
  { href: '/admin/audit/logs', label: 'Audit Trail', icon: '📊', badge: 'Admin' },
  { href: '/authz/debug', label: 'Authz Debugger', icon: '🧪', badge: 'QA' }
];

const userNavItems: NavItem[] = [
  { href: '/parcels', label: 'Parcels', icon: '🌱' },
  { href: '/establishments', label: 'Establishments', icon: '🏛️' },
  { href: '/crops', label: 'Crops', icon: '🌿' }
];

export default function NavigationMenu({ isAdmin = false }: { isAdmin?: boolean }) {
  const items = isAdmin ? [...userNavItems, ...adminNavItems] : userNavItems;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <span className="text-2xl font-bold text-green-600">🌱 VitiScan</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-4">
            {items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-green-50 hover:text-green-700 transition-colors"
              >
                {item.icon && <span className="mr-2">{item.icon}</span>}
                {item.label}
                {item.badge && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <button className="text-gray-700 hover:text-green-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
