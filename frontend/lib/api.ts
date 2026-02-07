import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (data: {
    username: string;
    password: string;
    language: string;
    role: string;
    accept_terms: boolean;
    accept_privacy: boolean;
    marketing_consent?: boolean;
    full_name?: string;
  }) => {
    const response = await api.post('/register', data);
    return response.data;
  },
  
  login: async (username: string, password: string) => {
    const response = await api.post('/login', { username, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/me');
    return response.data;
  },
};

// Establishments API
export const establishmentsAPI = {
  create: async (data: { name: string; siret: string; address: string; surface_ha: number }) => {
    const response = await api.post('/establishments', data);
    return response.data;
  },
  
  getMine: async () => {
    const response = await api.get('/establishments/mine');
    return response.data;
  },
};

// Parcels API
export const parcelsAPI = {
  create: async (data: { 
    name: string; 
    crop_type: string; 
    area_ha: number; 
    establishment_id: string;
    coordinates?: number[][][];
    planting_year?: number;
  }) => {
    const response = await api.post('/parcels', data);
    return response.data;
  },
  
  getById: async (parcel_id: string) => {
    const response = await api.get(`/parcels/${parcel_id}`);
    return response.data;
  },
  
  getByEstablishment: async (establishment_id: string) => {
    const response = await api.get(`/parcels/by-establishment/${establishment_id}`);
    return response.data;
  },
  
  update: async (parcel_id: string, data: any) => {
    const response = await api.put(`/parcels/${parcel_id}`, data);
    return response.data;
  },
  
  delete: async (parcel_id: string) => {
    const response = await api.delete(`/parcels/${parcel_id}`);
    return response.data;
  },

  exportDraaf: async (parcel_id: string) => {
    const response = await api.get(`/parcels/${parcel_id}/export`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Treatments API
export const treatmentsAPI = {
  listByParcel: async (parcel_id: string) => {
    const response = await api.get(`/parcels/${parcel_id}/treatments`);
    return response.data;
  },

  create: async (parcel_id: string, data: {
    data_tratament: string;
    tip_tratament: string;
    produs_utilizat: string;
    doza_aplicata: number;
    operator?: string;
    note_optionale?: string;
  }) => {
    const response = await api.post(`/parcels/${parcel_id}/treatments`, data);
    return response.data;
  },
};

// Crops API
export const cropsAPI = {
  create: async (data: { name: string; variety: string | null; year: number; parcel_id: string }) => {
    const response = await api.post('/crops', data);
    return response.data;
  },
  
  getByParcel: async (parcel_id: string) => {
    const response = await api.get(`/crops/by-parcel/${parcel_id}`);
    return response.data;
  },
  
  update: async (crop_id: string, data: any) => {
    const response = await api.put(`/crops/${crop_id}`, data);
    return response.data;
  },
  
  delete: async (crop_id: string) => {
    const response = await api.delete(`/crops/${crop_id}`);
    return response.data;
  },
};

// Scans API
export const scansAPI = {
  upload: async (parcel_id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/scans/${parcel_id}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getByParcel: async (parcel_id: string) => {
    const response = await api.get(`/scans/by-parcel/${parcel_id}`);
    return response.data;
  },
  
  download: async (scan_id: string) => {
    const response = await api.get(`/scans/${scan_id}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Invitations API
export const invitationsAPI = {
  listMembers: async () => {
    const response = await api.get('/invitations/members');
    return response.data;
  },

  listInvitations: async () => {
    const response = await api.get('/invitations/');
    return response.data;
  },

  createInvitation: async (data: { email: string; role: string; expires_in_days: number }) => {
    const response = await api.post('/invitations/', data);
    return response.data;
  },

  revokeInvitation: async (invitation_id: string) => {
    const response = await api.delete(`/invitations/${invitation_id}`);
    return response.data;
  },

  removeMember: async (member_id: string) => {
    const response = await api.delete(`/invitations/members/${member_id}`);
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  listBetaRequests: async () => {
    const response = await api.get('/admin/beta-requests');
    return response.data;
  },

  approveBetaRequest: async (request_id: string) => {
    const response = await api.post(`/admin/beta-requests/${request_id}/approve`);
    return response.data;
  },

  rejectBetaRequest: async (request_id: string) => {
    const response = await api.post(`/admin/beta-requests/${request_id}/reject`);
    return response.data;
  },

  getAuditLogs: async (params?: {
    limit?: number;
    user_id?: string;
    action?: string;
    outcome?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.user_id) query.append('user_id', params.user_id);
    if (params?.action) query.append('action', params.action);
    if (params?.outcome) query.append('outcome', params.outcome);
    if (params?.start_date) query.append('start_date', params.start_date);
    if (params?.end_date) query.append('end_date', params.end_date);

    const response = await api.get(`/admin/audit/logs?${query.toString()}`);
    return response.data;
  },

  getAuditStats: async (days = 7) => {
    const response = await api.get(`/admin/audit/stats?days=${days}`);
    return response.data;
  },

  getGlobalStats: async () => {
    const response = await api.get('/admin/global/stats');
    return response.data;
  },

  getRecentUsers: async (limit = 10) => {
    const response = await api.get(`/admin/global/recent-users?limit=${limit}`);
    return response.data;
  },
};

// Beta Requests API (public)
export const betaRequestsAPI = {
  create: async (data: {
    email: string;
    phone: string;
    name: string;
    farm_name: string;
    region?: string;
    reason?: string;
  }) => {
    const response = await api.post('/beta-request', data);
    return response.data;
  },

  verifyToken: async (token: string) => {
    const response = await api.get(`/beta-request/verify/${token}`);
    return response.data;
  },

  completeRegistration: async (token: string, password: string) => {
    const response = await api.post(`/beta-request/complete/${token}`, { password });
    return response.data;
  },

  completeRegistrationWithVerification: async (token: string, password: string, verificationCode: string) => {
    const response = await api.post(`/beta-request/complete/${token}`, { 
      password,
      verification_code: verificationCode 
    });
    return response.data;
  },
};

// AuthZ / Capability Tokens API
export const authzAPI = {
  createToken: async (data: {
    resource_type: string;
    resource_id: string;
    action: string;
    expires_in_hours?: number;
    subject_id?: string;
    max_uses?: number | null;
    description?: string;
  }) => {
    const response = await api.post('/authz/tokens/create', data);
    return response.data;
  },

  listTokens: async () => {
    const response = await api.get('/authz/tokens/list');
    return response.data;
  },

  revokeToken: async (token: string) => {
    const response = await api.delete(`/authz/tokens/revoke`, { params: { token } });
    return response.data;
  },

  revokeTokenById: async (tokenId: string) => {
    const response = await api.delete(`/authz/tokens/${tokenId}`);
    return response.data;
  },

  verifyToken: async (params: {
    token: string;
    resource_type: string;
    resource_id: string;
    action: string;
    subject_id?: string;
  }) => {
    const response = await api.post('/authz/tokens/verify', null, { params });
    return response.data;
  },

  inspectToken: async (token: string) => {
    const response = await api.get(`/authz/tokens/inspect/${token}`);
    return response.data;
  },

  getResourceByToken: async (token: string) => {
    const response = await api.get(`/authz/tokens/resource/${token}`);
    return response.data;
  },
};

// Billing API
export const billingAPI = {
  getUsage: async () => {
    const response = await api.get('/billing/usage');
    return response.data;
  },

  createCheckout: async (plan_id: string) => {
    const response = await api.post('/billing/create-checkout', { plan_id });
    return response.data;
  },
};
