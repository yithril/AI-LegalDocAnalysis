'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import ModalForm from '@/components/shared/ModalForm';
import type { CreateUserGroupRequest } from '@/types/api';

interface CreateUserGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateUserGroupModal({ isOpen, onClose, onSuccess }: CreateUserGroupModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  // Storage key for form persistence
  const STORAGE_KEY = 'create-user-group-form-data';
  
  const [groupName, setGroupName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-save form data to sessionStorage
  useEffect(() => {
    if (groupName) {
      const formData = { groupName };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
    }
  }, [groupName]);

  // Load saved form data when modal opens
  useEffect(() => {
    if (isOpen) {
      const savedData = sessionStorage.getItem(STORAGE_KEY);
      if (savedData) {
        try {
          const parsedData = JSON.parse(savedData);
          setGroupName(parsedData.groupName || '');
        } catch (error) {
          console.error('Error loading saved form data:', error);
          sessionStorage.removeItem(STORAGE_KEY);
        }
      }
    }
  }, [isOpen]);

  const clearSavedData = () => {
    sessionStorage.removeItem(STORAGE_KEY);
  };

  const handleCreateGroup = async () => {
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const createRequest: CreateUserGroupRequest = {
        name: groupName.trim()
      };

      await apiClient.createUserGroup(createRequest);

      // Clear saved data and reset form
      clearSavedData();
      setGroupName('');
      
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create group');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    clearSavedData();
    setGroupName('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h2 
            className="text-xl font-semibold mb-4"
            style={{ color: theme.textColor }}
          >
            Create New User Group
          </h2>

          <form onSubmit={(e) => { e.preventDefault(); handleCreateGroup(); }}>
            <ModalForm
              onCancel={handleCancel}
              submitText="Create Group"
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