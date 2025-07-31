'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import type { GetUserGroupResponse, GetProjectResponse } from '@/types/api';

interface ViewProjectGroupsModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: GetProjectResponse | null;
}

export default function ViewProjectGroupsModal({ isOpen, onClose, project }: ViewProjectGroupsModalProps) {
  const { user, isPM, isAdmin } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  const [assignedGroups, setAssignedGroups] = useState<GetUserGroupResponse[]>([]);
  const [availableGroups, setAvailableGroups] = useState<GetUserGroupResponse[]>([]);
  const [selectedGroupIds, setSelectedGroupIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const canManageGroups = isPM() || isAdmin();

  useEffect(() => {
    if (isOpen && project && user) {
      fetchProjectGroups();
      if (canManageGroups) {
        fetchAvailableGroups();
      }
    }
  }, [isOpen, project, user, canManageGroups]);

  const fetchProjectGroups = async () => {
    if (!project) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getUserGroupsForProject(project.id);
      setAssignedGroups(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project groups');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableGroups = async (search?: string) => {
    if (!project) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getUserGroupsNotInProject(project.id, search || '');
      setAvailableGroups(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch available groups');
    } finally {
      setLoading(false);
    }
  };

  const handleAddGroups = async () => {
    if (!project || selectedGroupIds.length === 0) return;
    
    try {
      setLoading(true);
      setError(null);

      // Add selected groups to the project
      for (const groupId of selectedGroupIds) {
        await apiClient.addUserGroupToProject(project.id, groupId);
      }

      // Refresh lists
      await fetchProjectGroups();
      await fetchAvailableGroups();
      
      // Reset selection
      setSelectedGroupIds([]);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add groups to project');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveGroup = async (groupId: number) => {
    if (!project) return;
    
    try {
      await apiClient.removeUserGroupFromProject(project.id, groupId);
      
      // Refresh the assigned groups list
      await fetchProjectGroups();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove group from project');
    }
  };

  const handleGroupToggle = (groupId: number) => {
    setSelectedGroupIds(prev => 
      prev.includes(groupId) 
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  const handleSearch = async (term: string) => {
    setSearchTerm(term);
    await fetchAvailableGroups(term);
  };

  const selectedGroups = availableGroups.filter(group => selectedGroupIds.includes(group.id));

  if (!isOpen || !project) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 
              className="text-xl font-semibold"
              style={{ color: theme.textColor }}
            >
              Manage Groups for: {project.name}
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

          {/* Project Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium mb-2">Project Information</h3>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Name:</span> {project.name}
              </div>
              <div>
                <span className="font-medium">Description:</span> {project.description || 'No description'}
              </div>
              <div>
                <span className="font-medium">Assigned Groups:</span> {assignedGroups.length} group{assignedGroups.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Assigned Groups Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Assigned Groups ({assignedGroups.length})</h3>
              
              {loading && (
                <div className="text-center py-4">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-sm text-gray-500">Loading groups...</p>
                </div>
              )}

              {!loading && assignedGroups.length === 0 && (
                <div className="text-center py-8 border border-gray-200 rounded-lg">
                  <div className="text-gray-400 mb-2">
                    <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <p className="text-gray-500">No groups assigned to this project</p>
                </div>
              )}

              {!loading && assignedGroups.length > 0 && (
                <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
                  {assignedGroups.map((group) => (
                    <div key={group.id} className="flex items-center justify-between p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {group.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">{group.name}</div>
                          <div className="text-sm text-gray-500">Created {new Date(group.created_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                      {canManageGroups && (
                        <button
                          type="button"
                          onClick={() => handleRemoveGroup(group.id)}
                          className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded hover:bg-red-50"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Add Groups Section (Admin/PM only) */}
            {canManageGroups && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Add Groups</h3>
                
                {/* Search */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Search Available Groups
                  </label>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => handleSearch(e.target.value)}
                    placeholder="Type to search groups..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Available Groups */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Available Groups ({availableGroups.length})
                  </label>
                  
                  <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
                    {availableGroups.length > 0 ? (
                      availableGroups.map((group) => (
                        <button
                          key={group.id}
                          type="button"
                          onClick={() => handleGroupToggle(group.id)}
                          className={`w-full text-left p-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 ${
                            selectedGroupIds.includes(group.id) ? 'bg-blue-50 border-blue-200' : ''
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                              <span className="text-gray-600 font-medium text-sm">
                                {group.name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <div className="font-medium">{group.name}</div>
                              <div className="text-sm text-gray-500">Created {new Date(group.created_at).toLocaleDateString()}</div>
                            </div>
                            {selectedGroupIds.includes(group.id) && (
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
                        {searchTerm ? 'No groups found' : 'No available groups'}
                      </div>
                    )}
                  </div>
                </div>

                {/* Selected Groups to Add */}
                {selectedGroups.length > 0 && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium mb-2">
                      Groups to Add ({selectedGroups.length})
                    </label>
                    <div className="max-h-40 overflow-y-auto border border-blue-200 rounded-lg p-2 bg-blue-50">
                      {selectedGroups.map((group) => (
                        <div key={group.id} className="flex justify-between items-center py-1">
                          <div>
                            <div className="font-medium">{group.name}</div>
                            <div className="text-sm text-gray-500">Created {new Date(group.created_at).toLocaleDateString()}</div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleGroupToggle(group.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Add Button */}
                {selectedGroups.length > 0 && (
                  <button
                    onClick={handleAddGroups}
                    disabled={loading}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {loading ? 'Adding...' : `Add ${selectedGroups.length} Group${selectedGroups.length !== 1 ? 's' : ''}`}
                  </button>
                )}
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