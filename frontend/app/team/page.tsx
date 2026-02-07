'use client';

import { useEffect, useState } from 'react';
import Breadcrumbs from '@/components/Breadcrumbs';
import { LoadingSpinner, ErrorAlert, SuccessAlert, EmptyState } from '@/components/UIComponents';
import { invitationsAPI } from '@/lib/api';

interface Member {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  joined_at: string;
  is_owner: boolean;
}

interface Invitation {
  id: string;
  establishment_id: string;
  establishment_name: string;
  email: string;
  role: string;
  status: string;
  invite_code: string;
  invited_by: string;
  created_at: string;
  expires_at: string;
}

export default function TeamManagementPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'member',
    expires_in_days: 7
  });

  useEffect(() => {
    loadTeamData();
  }, []);

  const loadTeamData = async () => {
    try {
      const [membersData, invitationsData] = await Promise.all([
        invitationsAPI.listMembers(),
        invitationsAPI.listInvitations(),
      ]);

      setMembers(membersData || []);
      setInvitations(invitationsData || []);
    } catch (error) {
      console.error('Error loading team data:', error);
      const message = (error as any)?.response?.data?.detail || 'Eroare la încărcarea echipei';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await invitationsAPI.createInvitation(inviteForm);

      setSuccess('Invitație trimisă cu succes!');
      setShowInviteForm(false);
      setInviteForm({ email: '', role: 'member', expires_in_days: 7 });
      await loadTeamData();
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Eroare la trimiterea invitației';
      setError(message);
    }
  };

  const handleRevokeInvite = async (inviteId: string) => {
    if (!confirm('Sigur vrei să revoci această invitație?')) return;

    try {
      await invitationsAPI.revokeInvitation(inviteId);
      setSuccess('Invitație revocată');
      await loadTeamData();
    } catch (error) {
      const message = (error as any)?.response?.data?.detail || 'Eroare la revocare invitație';
      setError(message);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!confirm('Sigur vrei să elimini acest membru din echipă?')) return;

    try {
      await invitationsAPI.removeMember(memberId);
      setSuccess('Membru eliminat');
      await loadTeamData();
    } catch (error) {
      const message = (error as any)?.response?.data?.detail || 'Eroare la eliminarea membrului';
      setError(message);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-100 text-purple-800';
      case 'admin': return 'bg-blue-100 text-blue-800';
      case 'consultant': return 'bg-green-100 text-green-800';
      case 'viewer': return 'bg-gray-100 text-gray-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      case 'revoked': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <LoadingSpinner />
      </div>
    );
  }

  const pendingInvites = invitations.filter(i => i.status === 'pending');

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <Breadcrumbs items={[
          { label: 'Echipă & Invitații' }
        ]} />

        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestionare Echipă</h1>
            <p className="text-gray-600 mt-2">Invită colaboratori și gestionează rolurile echipei</p>
          </div>
          <button
            onClick={() => setShowInviteForm(!showInviteForm)}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            + Invită membru
          </button>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess('')} />}

        {/* Invite Form */}
        {showInviteForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Invită membru nou</h2>
            <form onSubmit={handleInvite} className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rol
                  </label>
                  <select
                    value={inviteForm.role}
                    onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    <option value="viewer">Viewer (doar vizualizare)</option>
                    <option value="member">Member (acces complet)</option>
                    <option value="consultant">Consultant (expert extern)</option>
                    <option value="admin">Admin (management complet)</option>
                  </select>
                </div>
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  Trimite invitație
                </button>
                <button
                  type="button"
                  onClick={() => setShowInviteForm(false)}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Anulează
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Membri Activi</div>
            <div className="text-2xl font-bold text-gray-900">{members.length}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Invitații În Așteptare</div>
            <div className="text-2xl font-bold text-yellow-600">{pendingInvites.length}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Total Invitații</div>
            <div className="text-2xl font-bold text-gray-900">{invitations.length}</div>
          </div>
        </div>

        {/* Members List */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Membri Echipă ({members.length})</h2>
          
          {members.length === 0 ? (
            <EmptyState
              icon="👥"
              title="Nu există membri încă"
              description="Invită primul membru în echipa ta"
            />
          ) : (
            <div className="space-y-3">
              {members.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-600 font-semibold">
                        {member.full_name?.charAt(0) || '?'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium text-gray-900">{member.full_name}</p>
                        {member.is_owner && (
                          <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                            👑 Owner
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{member.email}</p>
                      <p className="text-xs text-gray-500">
                        Membru din {new Date(member.joined_at).toLocaleDateString('ro-RO')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(member.role)}`}>
                      {member.role}
                    </span>
                    {!member.is_owner && (
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Elimină
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Invitations List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Invitații ({invitations.length})</h2>
          
          {invitations.length === 0 ? (
            <EmptyState
              icon="📧"
              title="Nu există invitații"
              description="Invită membri pentru a colabora la fermă"
            />
          ) : (
            <div className="space-y-3">
              {invitations.map((invite) => (
                <div
                  key={invite.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <p className="font-medium text-gray-900">{invite.email}</p>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(invite.role)}`}>
                        {invite.role}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(invite.status)}`}>
                        {invite.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      Trimisă: {new Date(invite.created_at).toLocaleDateString('ro-RO')} • 
                      Expiră: {new Date(invite.expires_at).toLocaleDateString('ro-RO')}
                    </p>
                  </div>
                  
                  {invite.status === 'pending' && (
                    <button
                      onClick={() => handleRevokeInvite(invite.id)}
                      className="text-red-600 hover:text-red-700 text-sm font-medium"
                    >
                      Revocă
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
