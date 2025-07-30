'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import ModalForm from '@/components/shared/ModalForm';
import type { GetUserGroupResponse, UpdateUserGroupRequest } from '@/types/api';

interface EditUserGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  group: GetUserGroupResponse | null;
}

export default function EditUserGroupModal({ isOpen, onClose, onSuccess, group }: EditUserGroupModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  const [groupName, setGroupName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && group && user) {
      setGroupName(group.name);
    }
  }, [isOpen, group, user]);

  const handleUpdateGroup = async () => {
    if (!group) return;
    
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const updateRequest: UpdateUserGroupRequest = {
        name: groupName.trim()
      };

      await apiClient.updateUserGroup(group.id, updateRequest);
      
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
    setError(null);
    onClose();
  };

  if (!isOpen || !group) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h2 
            className="text-xl font-semibold mb-4"
            style={{ color: theme.textColor }}
          >
            Edit User Group
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