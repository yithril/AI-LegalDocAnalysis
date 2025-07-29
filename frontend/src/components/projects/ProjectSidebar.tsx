'use client'

import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'

interface ProjectSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
  projectId: number
}

export default function ProjectSidebar({ activeSection, onSectionChange, projectId }: ProjectSidebarProps) {
  const { isPM, isAdmin } = useAuth()
  const { theme } = useTheme()

  const canManageAccess = isPM() || isAdmin()

  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'documents', label: 'Documents', icon: '📄' },
    { id: 'actors', label: 'Actors', icon: '👥' },
    { id: 'timeline', label: 'Timeline', icon: '📅' },
    { id: 'ai-assistant', label: 'AI Assistant', icon: '🤖' },
  ]

  // Add management section for PM/Admin
  if (canManageAccess) {
    sections.push({ id: 'project-access', label: 'Project Access', icon: '⚙️' })
  }

  return (
    <div className="w-64 bg-white shadow-md rounded-lg p-4">
      <h3 
        className="text-lg font-semibold mb-4"
        style={{ color: theme.textColor }}
      >
        Project Sections
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