'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch';
import ModalForm from '@/components/shared/ModalForm';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface UserGroup {
  id: number;
  name: string;
  tenant_id: number;
  created_at: string;
  created_by?: string;
  updated_at: string;
  updated_by?: string;
}

interface EditUserGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  group: UserGroup | null;
}

export default function EditUserGroupModal({ isOpen, onClose, onSuccess, group }: EditUserGroupModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const { authenticatedFetch, hasToken } = useAuthenticatedFetch({
    onError: (error) => setError(error)
  });
  
  const [groupName, setGroupName] = useState('');
  const [currentUsers, setCurrentUsers] = useState<User[]>([]);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [showTypeahead, setShowTypeahead] = useState(false);

  useEffect(() => {
    if (isOpen && group && hasToken) {
      setGroupName(group.name);
      fetchGroupUsers();
      fetchAvailableUsers();
    }
  }, [isOpen, group, hasToken]);

  const fetchGroupUsers = async () => {
    if (!group) return;
    
    try {
      const response = await authenticatedFetch(`/api/user-groups/${group.id}/users`);
      const data = await response.json();
      setCurrentUsers(data.users || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch group users');
    }
  };

  const fetchAvailableUsers = async (search?: string) => {
    if (!group) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Get users not in this group
      const response = await authenticatedFetch(`/api/user-groups/${group.id}/available-users${search ? `?search_term=${encodeURIComponent(search)}` : ''}`);
      const data = await response.json();
      setAvailableUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch available users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (term: string) => {
    setSearchTerm(term);
    setIsSearching(true);
    
    // Debounce the search
    setTimeout(async () => {
      await fetchAvailableUsers(term);
      setIsSearching(false);
    }, 300);
  };

  const handleUpdateGroup = async () => {
    if (!group) return;
    
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Update the group name
      const updateResponse = await authenticatedFetch(`/api/user-groups/${group.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: groupName.trim()
        }),
      });

      if (!updateResponse.ok) {
        throw new Error('Failed to update group');
      }

      // Add selected users to the group
      for (const userId of selectedUserIds) {
        await authenticatedFetch(`/api/user-groups/${group.id}/users/${userId}`, {
          method: 'POST',
        });
      }

      // Reset form
      setSelectedUserIds([]);
      setSearchTerm('');
      setShowTypeahead(false);
      
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update group');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setGroupName('');
    setCurrentUsers([]);
    setSelectedUserIds([]);
    setSearchTerm('');
    setShowTypeahead(false);
    setError(null);
    onClose();
  };

  const handleUserToggle = (userId: number) => {
    setSelectedUserIds(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleRemoveUser = async (userId: number) => {
    if (!group) return;
    
    try {
      await authenticatedFetch(`/api/user-groups/${group.id}/users/${userId}`, {
        method: 'DELETE',
      });
      
      // Refresh the current users list
      await fetchGroupUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove user from group');
    }
  };

  const selectedUsers = availableUsers.filter(user => selectedUserIds.includes(user.id));

  if (!isOpen || !group) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 
            className="text-xl font-semibold mb-4"
            style={{ color: theme.textColor }}
          >
            Edit User Group: {group.name}
          </h2>

          <form onSubmit={(e) => { e.preventDefault(); handleUpdateGroup(); }}>
            <ModalForm
              onCancel={handleCancel}
              submitText="Update Group"
              isLoading={loading}
            >
              {/* Group Name */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Group Name
                </label>
                <input
                  type="text"
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  placeholder="Enter group name..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {/* Current Users */}
              {currentUsers.length > 0 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">
                    Current Users ({currentUsers.length})
                  </label>
                  <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-md p-2">
                    {currentUsers.map((user) => (
                      <div key={user.id} className="flex justify-between items-center py-1">
                        <div>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveUser(user.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Add Users */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Add Users</h3>
                
                {/* Initial Dropdown (first 10 users) */}
                {!showTypeahead && availableUsers.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Select Users to Add
                    </label>
                    <div className="max-h-60 overflow-y-auto border border-gray-300 rounded-md">
                      {availableUsers.slice(0, 10).map((user) => (
                        <button
                          key={user.id}
                          type="button"
                          onClick={() => handleUserToggle(user.id)}
                          className={`w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                            selectedUserIds.includes(user.id) ? 'bg-blue-50 text-blue-700' : ''
                          }`}
                        >
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </button>
                      ))}
                    </div>
                    
                    {/* Show "Search more" if there are more than 10 users */}
                    {availableUsers.length > 10 && (
                      <button
                        type="button"
                        onClick={() => setShowTypeahead(true)}
                        className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                      >
                        Search more users...
                      </button>
                    )}
                  </div>
                )}

                {/* Typeahead Search */}
                {showTypeahead && (
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Search Users to Add
                    </label>
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => handleSearch(e.target.value)}
                      placeholder="Type to search users..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    
                    {isSearching && (
                      <div className="mt-2 text-sm text-gray-500">Searching...</div>
                    )}
                    
                    {!isSearching && (
                      <div className="mt-2 max-h-60 overflow-y-auto border border-gray-300 rounded-md">
                        {availableUsers.length > 0 ? (
                          availableUsers.map((user) => (
                            <button
                              key={user.id}
                              type="button"
                              onClick={() => handleUserToggle(user.id)}
                              className={`w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                                selectedUserIds.includes(user.id) ? 'bg-blue-50 text-blue-700' : ''
                              }`}
                            >
                              <div className="font-medium">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </button>
                          ))
                        ) : (
                          <div className="px-4 py-2 text-gray-500">No users found</div>
                        )}
                      </div>
                    )}
                    
                    <button
                      type="button"
                      onClick={() => setShowTypeahead(false)}
                      className="mt-2 text-sm text-gray-600 hover:text-gray-800"
                    >
                      ← Back to dropdown
                    </button>
                  </div>
                )}

                {/* Show dropdown if no typeahead and no users in dropdown */}
                {!showTypeahead && availableUsers.length === 0 && !loading && (
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Search Users to Add
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowTypeahead(true)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-left text-gray-500 hover:bg-gray-50"
                    >
                      Click to search users...
                    </button>
                  </div>
                )}

                {/* Selected Users Display */}
                {selectedUsers.length > 0 && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium mb-2">
                      Users to Add ({selectedUsers.length})
                    </label>
                    <div className="max-h-40 overflow-y-auto border border-gray-300 rounded-md p-2">
                      {selectedUsers.map((user) => (
                        <div key={user.id} className="flex justify-between items-center py-1">
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleUserToggle(user.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}
            </ModalForm>
          </form>
        </div>
      </div>
    </div>
  );
} 