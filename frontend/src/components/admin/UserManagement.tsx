'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch'
import { getRoleDisplayName } from '@/lib/roles'

interface User {
  id: number
  nextauth_user_id: string
  email: string
  name: string
  role: string
  tenant_id: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
}

interface UserManagementProps {
  className?: string
}

export default function UserManagement({ className = '' }: UserManagementProps) {
  const { isAdmin } = useAuth()
  const { theme } = useTheme()
  const { authenticatedFetch } = useAuthenticatedFetch()

  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updatingUserId, setUpdatingUserId] = useState<number | null>(null)
  const [selectedRoles, setSelectedRoles] = useState<Record<number, string>>({})

  // Don't render anything if user is not admin
  if (!isAdmin()) {
    return null
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await authenticatedFetch('/api/users/')
      const data = await response.json()
      setUsers(data)
      
      // Initialize selected roles with current user roles
      const initialRoles: Record<number, string> = {}
      data.forEach((user: User) => {
        initialRoles[user.id] = user.role
      })
      setSelectedRoles(initialRoles)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = (userId: number, newRole: string) => {
    setSelectedRoles(prev => ({
      ...prev,
      [userId]: newRole
    }))
  }

  const handleUpdateRole = async (userId: number) => {
    const newRole = selectedRoles[userId]
    if (!newRole) {
      setError('Please select a role')
      return
    }

    try {
      setUpdatingUserId(userId)
      setError(null)

      await authenticatedFetch(`/api/users/${userId}/role`, {
        method: 'PATCH',
        body: JSON.stringify({ role: newRole })
      })

      // Update the user in the list
      setUsers(prev => prev.map(user => 
        user.id === userId 
          ? { ...user, role: newRole }
          : user
      ))

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user role')
    } finally {
      setUpdatingUserId(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
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
            onClick={fetchUsers}
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
        <h2
          className="text-2xl font-bold"
          style={{ color: theme.textColor }}
        >
          User Management
        </h2>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-8">
          <p style={{ color: theme.secondaryColor }}>No users found.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 rounded-lg">
            <thead>
              <tr style={{ backgroundColor: theme.backgroundColor }}>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>User</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Email</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Current Role</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>New Role</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Created</span>
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user, index) => (
                <tr
                  key={user.id}
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium" style={{ color: theme.textColor }}>
                      {user.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {user.email}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className="inline-block px-3 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: theme.accentColor,
                        color: 'white'
                      }}
                    >
                      {getRoleDisplayName(user.role)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={selectedRoles[user.id] || user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={updatingUserId === user.id}
                    >
                      <option value="viewer">Viewer</option>
                      <option value="analyst">Analyst</option>
                      <option value="pm">Project Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {formatDate(user.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleUpdateRole(user.id)}
                      disabled={updatingUserId === user.id || selectedRoles[user.id] === user.role}
                      className="px-3 py-1 rounded text-xs text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {updatingUserId === user.id ? 'Updating...' : 'Update'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
} 