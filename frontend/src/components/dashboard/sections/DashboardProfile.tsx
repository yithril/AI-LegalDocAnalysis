'use client'

import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { getRoleDisplayName } from '@/lib/roles'

export default function DashboardProfile() {
  const { user, userRole } = useAuth()
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Profile Information
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Name
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {user?.name || 'Not provided'}
            </p>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Email
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {user?.email || 'Not provided'}
            </p>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Role
            </h3>
            <span
              className="inline-block px-3 py-1 rounded-full text-xs font-medium"
              style={{ 
                backgroundColor: theme.accentColor,
                color: 'white'
              }}
            >
              {getRoleDisplayName(userRole)}
            </span>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              User ID
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {user?.id || 'Not available'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Account Settings
        </h2>
        <p
          className="text-sm"
          style={{ color: theme.secondaryColor }}
        >
          Account settings and preferences coming soon...
        </p>
      </div>
    </div>
  )
} 