'use client'

import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { getRoleDisplayName, isPM, isAdmin } from '@/lib/roles'

interface FeatureCardProps {
  title: string
  subtitle: string
  description: string
  onClick: () => void
  icon?: string
}

interface DashboardOverviewProps {
  onSectionChange: (section: string) => void
}

export default function DashboardOverview({ onSectionChange }: DashboardOverviewProps) {
  const { user, userRole } = useAuth()
  const { theme } = useTheme()

  const FeatureCard = ({ title, subtitle, description, onClick, icon }: FeatureCardProps) => (
    <button
      onClick={onClick}
      className="w-full bg-white rounded-lg shadow-md p-6 text-left transition-all duration-200 hover:shadow-lg hover:scale-105 cursor-pointer border border-transparent hover:border-gray-200"
    >
      <div className="flex items-center justify-between mb-4">
        <h3
          className="text-lg font-semibold"
          style={{ color: theme.textColor }}
        >
          {title}
        </h3>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <p
        className="text-2xl font-bold mb-2"
        style={{ color: theme.accentColor }}
      >
        {subtitle}
      </p>
      <p className="text-sm" style={{ color: theme.secondaryColor }}>
        {description}
      </p>
    </button>
  )

  return (
    <div className="space-y-6">
      {/* Welcome Card */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Welcome to your Dashboard
        </h2>
        
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold mb-2" style={{ color: theme.textColor }}>
            User Information
          </h3>
          <div className="space-y-2 text-sm" style={{ color: theme.secondaryColor }}>
            <p><strong>Name:</strong> {user?.name || 'N/A'}</p>
            <p><strong>Email:</strong> {user?.email || 'N/A'}</p>
            <p><strong>Role:</strong> {getRoleDisplayName(userRole)}</p>
            <p><strong>User ID:</strong> {user?.id || 'N/A'}</p>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Getting Started
          </h3>
          <p className="text-blue-700">
            Use the sidebar to navigate between different sections of your dashboard.
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          title="Projects"
          subtitle="View Projects"
          description="Access and manage your projects"
          icon="📁"
          onClick={() => onSectionChange('projects')}
        />

        <FeatureCard
          title="Groups"
          subtitle="My Groups"
          description="View your group memberships"
          icon="👥"
          onClick={() => onSectionChange('my-groups')}
        />

        <FeatureCard
          title="Profile"
          subtitle="Account Info"
          description="Manage your account settings"
          icon="👤"
          onClick={() => onSectionChange('profile')}
        />
      </div>

      {/* Admin Features */}
      {(isPM() || isAdmin()) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <FeatureCard
            title="User Groups"
            subtitle="Manage Groups"
            description="Create and manage user groups"
            icon="🔧"
            onClick={() => onSectionChange('user-groups')}
          />

          {isAdmin() && (
            <FeatureCard
              title="User Management"
              subtitle="Manage Users"
              description="Manage user roles and permissions"
              icon="⚙️"
              onClick={() => onSectionChange('user-management')}
            />
          )}
        </div>
      )}
    </div>
  )
} 