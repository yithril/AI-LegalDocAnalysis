'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch'
import AddGroupModal from './AddGroupModal'

interface UserGroup {
  id: number
  name: string
  tenant_id: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
}

interface ProjectAccessProps {
  projectId: number
  className?: string
}

export default function ProjectAccess({ projectId, className = '' }: ProjectAccessProps) {
  const { user, isPM, isAdmin } = useAuth()
  const { theme } = useTheme()
  const { authenticatedFetch } = useAuthenticatedFetch()

  const [groups, setGroups] = useState<UserGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [removingGroupId, setRemovingGroupId] = useState<number | null>(null)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  const canManageAccess = isPM() || isAdmin()

  useEffect(() => {
    if (canManageAccess) {
      fetchProjectGroups()
    }
  }, [projectId, canManageAccess])

  const fetchProjectGroups = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await authenticatedFetch(`/api/projects/${projectId}/groups`)
      const data = await response.json()
      setGroups(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project groups')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveGroup = async (groupId: number) => {
    if (!confirm('Are you sure you want to remove this group from the project?')) {
      return
    }

    try {
      setRemovingGroupId(groupId)

      await authenticatedFetch(`/api/projects/${projectId}/groups/${groupId}`, {
        method: 'DELETE',
      })

      // Remove the group from the list
      setGroups(groups.filter(group => group.id !== groupId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove group from project')
    } finally {
      setRemovingGroupId(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const handleAddSuccess = () => {
    fetchProjectGroups()
  }

  // Don't show anything if user can't manage access
  if (!canManageAccess) {
    return null
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchProjectGroups}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex justify-between items-center mb-6">
        <h3
          className="text-lg font-semibold"
          style={{ color: theme.textColor }}
        >
          Project Access
        </h3>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-3 py-1 text-sm text-white rounded-md hover:opacity-90 transition-opacity"
          style={{ backgroundColor: theme.accentColor }}
        >
          + Add Group
        </button>
      </div>

      {groups.length === 0 ? (
        <div className="text-center py-8">
          <p style={{ color: theme.secondaryColor }}>
            No groups have access to this project yet.
          </p>
          <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
            Add groups to grant access to project resources.
          </p>
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
                  <span style={{ color: theme.textColor }}>Added</span>
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
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleRemoveGroup(group.id)}
                      disabled={removingGroupId === group.id}
                      className="px-3 py-1 rounded text-xs text-red-600 hover:text-red-900 disabled:opacity-50"
                    >
                      {removingGroupId === group.id ? 'Removing...' : 'Remove'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Group Modal */}
      <AddGroupModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={handleAddSuccess}
        projectId={projectId}
      />
    </div>
  )
} 