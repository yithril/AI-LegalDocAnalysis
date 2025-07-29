'use client';

import { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch';

interface UserGroup {
  id: number;
  name: string;
  tenant_id: number;
  created_at: string;
  created_by?: string;
  updated_at: string;
  updated_by?: string;
}

interface UserGroupsListProps {
  onViewGroup?: (groupId: number) => void;
  onEditGroup?: (group: UserGroup) => void;
  onCreateGroup?: () => void;
  onRefresh?: () => void;
}

const UserGroupsList = forwardRef<{ refresh: () => void }, UserGroupsListProps>(({ 
  onViewGroup, 
  onEditGroup, 
  onCreateGroup
}, ref) => {
  const { user, isAdmin } = useAuth();
  const { theme } = useTheme();
  const { authenticatedFetch, hasToken } = useAuthenticatedFetch({
    onError: (error) => setError(error)
  });
  const [groups, setGroups] = useState<UserGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingGroupId, setDeletingGroupId] = useState<number | null>(null);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authenticatedFetch('/api/user-groups/');
      const data = await response.json();
      setGroups(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch groups');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGroup = async (groupId: number) => {
    if (!confirm('Are you sure you want to delete this group? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingGroupId(groupId);
      
      await authenticatedFetch(`/api/user-groups/${groupId}`, {
        method: 'DELETE',
      });

      // Remove the group from the list
      setGroups(groups.filter(group => group.id !== groupId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete group');
    } finally {
      setDeletingGroupId(null);
    }
  };

  // Fetch groups when component mounts or when admin status changes
  useEffect(() => {
    if (isAdmin && hasToken) {
      fetchGroups();
    }
  }, [isAdmin, hasToken]);

  // Expose refresh function to parent
  useImperativeHandle(ref, () => ({
    refresh: fetchGroups
  }));

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (!isAdmin) {
    return (
      <div className="p-6">
        <p style={{ color: theme.textColor }}>You don't have permission to manage user groups.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6">
        <p style={{ color: theme.textColor }}>Loading user groups...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-red-600">Error: {error}</p>
        <button 
          onClick={fetchGroups}
          className="mt-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 
          className="text-2xl font-bold"
          style={{ color: theme.textColor }}
        >
          User Groups
        </h2>
        <button
          onClick={onCreateGroup}
          className="px-4 py-2 text-white rounded-md hover:opacity-90 transition-opacity"
          style={{ backgroundColor: theme.accentColor }}
        >
          + Add Group
        </button>
      </div>

      {groups.length === 0 ? (
        <div className="text-center py-8">
          <p style={{ color: theme.secondaryColor }}>No user groups found.</p>
          <p className="mt-2" style={{ color: theme.secondaryColor }}>Create your first group to get started.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 rounded-lg">
            <thead>
              <tr style={{ backgroundColor: theme.backgroundColor }}>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Group Name</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Created</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Updated</span>
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {groups.map((group, index) => (
                <tr 
                  key={group.id} 
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium" style={{ color: theme.textColor }}>
                      {group.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {formatDate(group.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {formatDate(group.updated_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => onViewGroup?.(group.id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </button>
                      <button
                        onClick={() => onEditGroup?.(group)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteGroup(group.id)}
                        disabled={deletingGroupId === group.id}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50"
                      >
                        {deletingGroupId === group.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
});

export default UserGroupsList; 