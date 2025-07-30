'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import type { GetUserResponse, GetUserGroupResponse } from '@/types/api';

interface ViewGroupDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  group: GetUserGroupResponse | null;
}

export default function ViewGroupDetailsModal({ isOpen, onClose, group }: ViewGroupDetailsModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  const [currentUsers, setCurrentUsers] = useState<GetUserResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && group && user) {
      fetchGroupUsers();
    }
  }, [isOpen, group, user]);

  const fetchGroupUsers = async () => {
    if (!group) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getUsersInGroup(group.id);
      setCurrentUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch group users');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !group) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 
              className="text-xl font-semibold"
              style={{ color: theme.textColor }}
            >
              Group Details: {group.name}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Group Information */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-2">Group Information</h3>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Name:</span> {group.name}
              </div>
              <div>
                <span className="font-medium">Created:</span> {new Date(group.created_at).toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Members:</span> {currentUsers.length} user{currentUsers.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>

          {/* Current Users */}
          <div className="mb-4">
            <h3 className="text-lg font-medium mb-3">Group Members</h3>
            
            {loading && (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-500">Loading members...</p>
              </div>
            )}

            {!loading && currentUsers.length === 0 && (
              <div className="text-center py-8">
                <div className="text-gray-400 mb-2">
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                </div>
                <p className="text-gray-500">No members in this group</p>
              </div>
            )}

            {!loading && currentUsers.length > 0 && (
              <div className="space-y-2">
                {currentUsers.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
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
                    <div className="text-sm text-gray-500">
                      {user.role}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Close Button */}
          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 