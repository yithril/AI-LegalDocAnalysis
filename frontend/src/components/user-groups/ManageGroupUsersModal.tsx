'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import ModalForm from '@/components/shared/ModalForm';
import type { GetUserResponse, GetUserGroupResponse } from '@/types/api';

interface ManageGroupUsersModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  group: GetUserGroupResponse | null;
}

export default function ManageGroupUsersModal({ isOpen, onClose, onSuccess, group }: ManageGroupUsersModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  const [currentUsers, setCurrentUsers] = useState<GetUserResponse[]>([]);
  const [availableUsers, setAvailableUsers] = useState<GetUserResponse[]>([]);
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (isOpen && group && user) {
      fetchGroupUsers();
      fetchAvailableUsers();
    }
  }, [isOpen, group, user]);

  const fetchGroupUsers = async () => {
    if (!group) return;
    
    try {
      const data = await apiClient.getUsersInGroup(group.id);
      setCurrentUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch group users');
    }
  };

  const fetchAvailableUsers = async (search?: string) => {
    if (!group) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiClient.getUsersNotInGroup(group.id, search || '');
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
    
    setTimeout(async () => {
      await fetchAvailableUsers(term);
      setIsSearching(false);
    }, 300);
  };

  const handleAddUsers = async () => {
    if (!group || selectedUserIds.length === 0) return;
    
    try {
      setLoading(true);
      setError(null);

      // Add selected users to the group
      for (const userId of selectedUserIds) {
        await apiClient.addUserToGroup(userId, group.id);
      }

      // Refresh lists
      await fetchGroupUsers();
      await fetchAvailableUsers();
      
      // Reset selection
      setSelectedUserIds([]);
      
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add users to group');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveUser = async (userId: number) => {
    if (!group) return;
    
    try {
      await apiClient.removeUserFromGroup(userId, group.id);
      
      // Refresh the current users list
      await fetchGroupUsers();
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove user from group');
    }
  };

  const handleUserToggle = (userId: number) => {
    setSelectedUserIds(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleCancel = () => {
    setCurrentUsers([]);
    setAvailableUsers([]);
    setSelectedUserIds([]);
    setSearchTerm('');
    setError(null);
    onClose();
  };

  const selectedUsers = availableUsers.filter(user => selectedUserIds.includes(user.id));

  if (!isOpen || !group) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 
            className="text-xl font-semibold mb-4"
            style={{ color: theme.textColor }}
          >
            Manage Group Users: {group.name}
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current Users Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Current Members ({currentUsers.length})</h3>
              
              {currentUsers.length === 0 ? (
                <div className="text-center py-8 border border-gray-200 rounded-lg">
                  <div className="text-gray-400 mb-2">
                    <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <p className="text-gray-500">No members in this group</p>
                </div>
              ) : (
                <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
                  {currentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveUser(user.id)}
                        className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded hover:bg-red-50"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Add Users Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Add New Members</h3>
              
              {/* Search */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Search Users
                </label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Type to search users..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Available Users */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Available Users ({availableUsers.length})
                </label>
                
                {isSearching && (
                  <div className="text-center py-4">
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <p className="mt-1 text-sm text-gray-500">Searching...</p>
                  </div>
                )}

                {!isSearching && (
                  <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
                    {availableUsers.length > 0 ? (
                      availableUsers.map((user) => (
                        <button
                          key={user.id}
                          type="button"
                          onClick={() => handleUserToggle(user.id)}
                          className={`w-full text-left p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 ${
                            selectedUserIds.includes(user.id) ? 'bg-blue-50 border-blue-200' : ''
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                              <span className="text-gray-600 font-medium text-sm">
                                {user.name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <div className="font-medium">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                            {selectedUserIds.includes(user.id) && (
                              <div className="ml-auto">
                                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              </div>
                            )}
                          </div>
                        </button>
                      ))
                    ) : (
                      <div className="p-4 text-center text-gray-500">
                        {searchTerm ? 'No users found' : 'No available users'}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Selected Users to Add */}
              {selectedUsers.length > 0 && (
                <div className="mt-4">
                  <label className="block text-sm font-medium mb-2">
                    Users to Add ({selectedUsers.length})
                  </label>
                  <div className="max-h-40 overflow-y-auto border border-blue-200 rounded-lg p-2 bg-blue-50">
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
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 flex justify-end space-x-3">
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            {selectedUserIds.length > 0 && (
              <button
                onClick={handleAddUsers}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Adding...' : `Add ${selectedUserIds.length} User${selectedUserIds.length !== 1 ? 's' : ''}`}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 