// Type definitions for authorization system

export interface Subject {
  user_id: string;
  role?: 'admin' | 'user' | 'consultant' | 'agronom';
  mfa_enabled?: boolean;
  region?: string;
  certification_level?: number;
  [key: string]: any;
}

export interface Resource {
  type: 'parcel' | 'establishment' | 'crop' | 'scan';
  id: string;
  owner_id?: string;
  attributes?: {
    region?: string;
    high_risk?: boolean;
    certified?: boolean;
    [key: string]: any;
  };
}

export interface AuthzRequest {
  subject: Subject;
  resource: Resource;
  action: 'read' | 'write' | 'delete' | 'share';
}

export interface AuthzResponse {
  allowed: boolean;
  mechanism?: 'rbac' | 'abac' | 'rebac';
  matched_rules?: string[];
  explanation: string;
  dry_run?: boolean;
}

export interface Relationship {
  id?: string;
  subject_id: string;
  relation: 'owner' | 'consultant' | 'viewer' | 'collaborator' | 'auditor';
  resource_type: string;
  resource_id: string;
  created_at?: string;
}

export interface AuditLog {
  timestamp: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  outcome: 'allow' | 'deny';
  mechanism?: string;
  details?: any;
}

export interface CapabilityToken {
  token?: string; // Only returned on creation
  resource_type: string;
  resource_id: string;
  action: string;
  created_by: string;
  expires_at: string;
  max_uses?: number;
  uses_count?: number;
  target_subject?: string;
  revoked?: boolean;
}

export interface BetaRequest {
  id?: string;
  email: string;
  phone: string;
  full_name: string;
  company?: string;
  region?: string;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  created_at?: string;
  processed_at?: string;
  register_token?: string;
}
