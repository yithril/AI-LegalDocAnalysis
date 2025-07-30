'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useApiClient } from '@/lib/api-client'
import Modal from '@/components/shared/Modal'
import ModalForm from '@/components/shared/ModalForm'
import type { GetUserGroupResponse } from '@/types/api'

interface AddGroupModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  projectId: number
}

export default function AddGroupModal({ isOpen, onClose, onSuccess, projectId }: AddGroupModalProps) {
  const { isPM, isAdmin } = useAuth()
  const { theme } = useTheme()
  const apiClient = useApiClient()

  const [availableGroups, setAvailableGroups] = useState<GetUserGroupResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null)
  const [showTypeahead, setShowTypeahead] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canManageAccess = isPM() || isAdmin()

  // Don't render anything if user can't manage access
  if (!canManageAccess) {
    return null
  }

  useEffect(() => {
    if (isOpen && canManageAccess) {
      fetchAvailableGroups()
    }
  }, [isOpen, canManageAccess])

  const fetchAvailableGroups = async (search?: string) => {
    try {
      setLoading(true)
      setError(null)

      const data = await apiClient.getUserGroupsNotInProject(projectId, search || '')
      setAvailableGroups(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch available groups')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (term: string) => {
    setSearchTerm(term)
    setIsSearching(true)
    
    // Debounce the search
    setTimeout(async () => {
      await fetchAvailableGroups(term)
      setIsSearching(false)
    }, 300)
  }

  const handleAddGroup = async () => {
    if (!selectedGroupId) {
      setError('Please select a group')
      return
    }

    try {
      setLoading(true)
      setError(null)

      await apiClient.addUserGroupToProject(projectId, selectedGroupId)

      onSuccess()
      onClose()
      setSelectedGroupId(null)
      setSearchTerm('')
      setShowTypeahead(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add group to project')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setSelectedGroupId(null)
    setSearchTerm('')
    setShowTypeahead(false)
    setError(null)
    onClose()
  }

  const handleGroupSelect = (groupId: number) => {
    setSelectedGroupId(groupId)
    setShowTypeahead(false)
  }

  const selectedGroup = availableGroups.find(group => group.id === selectedGroupId)

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title="Add Group to Project"
      size="md"
    >
      <form onSubmit={(e) => { e.preventDefault(); handleAddGroup(); }}>
        <ModalForm
          onCancel={handleCancel}
          submitText="Add Group"
          isLoading={loading}
        >
        {/* Hybrid Dropdown/Typeahead */}
        <div className="space-y-4">
          {/* Initial Dropdown (first 10 groups) */}
          {!showTypeahead && availableGroups.length > 0 && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Select a Group
              </label>
              <div className="max-h-60 overflow-y-auto border border-gray-300 rounded-md">
                {availableGroups.slice(0, 10).map((group) => (
                  <button
                    key={group.id}
                    type="button"
                    onClick={() => handleGroupSelect(group.id)}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                      selectedGroupId === group.id ? 'bg-blue-50 text-blue-700' : ''
                    }`}
                  >
                    <div className="font-medium">{group.name}</div>
                  </button>
                ))}
              </div>
              
              {/* Show "Search more" if there are more than 10 groups */}
              {availableGroups.length > 10 && (
                <button
                  type="button"
                  onClick={() => setShowTypeahead(true)}
                  className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  Search more groups...
                </button>
              )}
            </div>
          )}

          {/* Typeahead Search */}
          {showTypeahead && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Search Groups
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Type to search groups..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              {isSearching && (
                <div className="mt-2 text-sm text-gray-500">Searching...</div>
              )}
              
              {!isSearching && searchTerm && (
                <div className="mt-2 max-h-60 overflow-y-auto border border-gray-300 rounded-md">
                  {availableGroups.length > 0 ? (
                    availableGroups.map((group) => (
                      <button
                        key={group.id}
                        type="button"
                        onClick={() => handleGroupSelect(group.id)}
                        className={`w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                          selectedGroupId === group.id ? 'bg-blue-50 text-blue-700' : ''
                        }`}
                      >
                        <div className="font-medium">{group.name}</div>
                      </button>
                    ))
                  ) : (
                    <div className="px-4 py-2 text-gray-500">No groups found</div>
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

          {/* Show dropdown if no typeahead and no groups in dropdown */}
          {!showTypeahead && availableGroups.length === 0 && !loading && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Search Groups
              </label>
              <button
                type="button"
                onClick={() => setShowTypeahead(true)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-left text-gray-500 hover:bg-gray-50"
              >
                Click to search groups...
              </button>
            </div>
          )}

          {/* Selected Group Display */}
          {selectedGroup && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <div className="text-sm font-medium text-green-800">
                Selected: {selectedGroup.name}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-2 text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && !isSearching && (
            <div className="mt-2 text-sm text-gray-500">
              Loading available groups...
            </div>
          )}
        </div>
        </ModalForm>
      </form>
    </Modal>
  )
} 