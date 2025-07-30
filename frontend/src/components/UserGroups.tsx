'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { getRoleDisplayName } from '@/lib/roles'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useApiClient } from '@/lib/api-client'
import type { GetUserGroupResponse } from '@/types/api'

interface UserGroupsProps {
  className?: string
}

export default function UserGroups({ className = '' }: UserGroupsProps) {
  const [userGroups, setUserGroups] = useState<GetUserGroupResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  const { user, userRole } = useAuth()
  const { theme } = useTheme()
  const apiClient = useApiClient()

  useEffect(() => {
    if (user) {
      fetchUserGroups()
    }
  }, [user])

  const fetchUserGroups = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getMyGroups()
      setUserGroups(data)
    } catch (err) {
      setError('Failed to load user groups')
      console.error('Error fetching user groups:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString()
  }

  if (isLoading) {
    return (
      <div className={`flex justify-center items-center py-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={fetchUserGroups}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 
          className="text-2xl font-bold mb-4"
          style={{ color: theme.textColor }}
        >
          My Account Information
        </h2>
        
        {/* User Role Section */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 
            className="text-lg font-semibold mb-2"
            style={{ color: theme.textColor }}
          >
            System Role
          </h3>
          <p 
            className="text-sm"
            style={{ color: theme.secondaryColor }}
          >
            Your system role determines what actions you can perform across the platform.
          </p>
          <div className="mt-2">
            <span 
              className="inline-block px-3 py-1 rounded-full text-sm font-medium"
              style={{ 
                backgroundColor: theme.accentColor,
                color: 'white'
              }}
            >
              {getRoleDisplayName(userRole)}
            </span>
          </div>
        </div>
      </div>

      {/* Groups Section */}
      <div>
        <h3 
          className="text-lg font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Group Memberships
        </h3>
        <p 
          className="text-sm mb-4"
          style={{ color: theme.secondaryColor }}
        >
          You have access to projects based on your group memberships.
        </p>

        {/* Groups Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200 rounded-lg">
            <thead>
              <tr style={{ backgroundColor: theme.backgroundColor }}>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Group Name</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Created</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Last Updated</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {userGroups.map((group, index) => (
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
                </tr>
              ))}
            </tbody>
          </table>

          {userGroups.length === 0 && (
            <div className="text-center py-8">
              <p style={{ color: theme.secondaryColor }}>
                You are not a member of any groups yet. Contact your administrator to be added to groups.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 