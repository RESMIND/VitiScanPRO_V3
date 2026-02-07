'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-4">
      <Link href="/dashboard" className="hover:text-gray-900 transition-colors">
        🏠 Dashboard
      </Link>
      
      {items.map((item, index) => (
        <div key={index} className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          
          {item.href ? (
            <Link href={item.href} className="hover:text-gray-900 transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-900 font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}

// Helper function to generate breadcrumbs from pathname
export function useBreadcrumbs(customItems?: BreadcrumbItem[]): BreadcrumbItem[] {
  const pathname = usePathname();
  
  if (customItems) {
    return customItems;
  }

  const segments = pathname?.split('/').filter(Boolean) || [];
  const breadcrumbs: BreadcrumbItem[] = [];

  const labels: Record<string, string> = {
    'establishments': 'Exploatații',
    'parcels': 'Parcele',
    'scans': 'Scanări',
    'admin': 'Admin',
    'settings': 'Setări',
    'beta-requests': 'Beta Requests',
    'audit': 'Audit',
    'logs': 'Logs',
    'profile': 'Profil',
    'security': 'Securitate',
    'tokens': 'Tokens',
    'new': 'Nou',
    'share': 'Share',
    'authz': 'Authorization',
    'debug': 'Debug'
  };

  let path = '';
  segments.forEach((segment, index) => {
    path += `/${segment}`;
    
    // Skip IDs (assume they're UUIDs or similar)
    if (segment.match(/^[a-f0-9-]{8,}$/i) || segment.startsWith('[')) {
      breadcrumbs.push({
        label: 'Detalii',
        href: index === segments.length - 1 ? undefined : path
      });
    } else {
      breadcrumbs.push({
        label: labels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1),
        href: index === segments.length - 1 ? undefined : path
      });
    }
  });

  return breadcrumbs;
}
