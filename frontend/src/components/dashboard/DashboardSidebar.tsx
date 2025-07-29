'use client'

import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'

interface DashboardSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

export default function DashboardSidebar({ activeSection, onSectionChange }: DashboardSidebarProps) {
  const { isPM, isAdmin } = useAuth()
  const { theme } = useTheme()

  const canManageGroups = isPM() || isAdmin()
  const canManageUsers = isAdmin()

  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'my-groups', label: 'My Groups', icon: '👥' },
    { id: 'profile', label: 'Profile', icon: '👤' },
  ]

  // Add management sections for PM/Admin
  if (canManageGroups) {
    sections.push({ id: 'user-groups', label: 'User Groups', icon: '🔧' })
  }

  // Add admin-only sections
  if (canManageUsers) {
    sections.push({ id: 'user-management', label: 'User Management', icon: '⚙️' })
  }

  return (
    <div className="w-64 bg-white shadow-md rounded-lg p-4">
      <h3 
        className="text-lg font-semibold mb-4"
        style={{ color: theme.textColor }}
      >
        Dashboard
      </h3>
      
      <nav className="space-y-2">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => onSectionChange(section.id)}
            className={`w-full text-left px-4 py-3 rounded-md transition-colors ${
              activeSection === section.id
                ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-500'
                : 'hover:bg-gray-50'
            }`}
            style={{ 
              color: activeSection === section.id ? undefined : theme.textColor 
            }}
          >
            <div className="flex items-center space-x-3">
              <span className="text-lg">{section.icon}</span>
              <span className="font-medium">{section.label}</span>
            </div>
          </button>
        ))}
      </nav>
    </div>
  )
} 