'use client'

import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useRouter } from 'next/navigation'

interface ProjectSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
  projectId: number
  hasContentAccess: boolean
}

export default function ProjectSidebar({ activeSection, onSectionChange, projectId, hasContentAccess }: ProjectSidebarProps) {
  const { isPM, isAdmin, isAnalyst } = useAuth()
  const { theme } = useTheme()
  const router = useRouter()

  const canManageAccess = isPM() || isAdmin()
  const canReviewDocuments = isPM() || isAdmin() || isAnalyst()

  // Always show Overview (general project info)
  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊', access: 'always' }
  ]

  // Content sections - only visible to group members
  if (hasContentAccess) {
    sections.push(
      { id: 'documents', label: 'Documents', icon: '📄', access: 'content' },
      { id: 'actors', label: 'Actors', icon: '👥', access: 'content' },
      { id: 'timeline', label: 'Timeline', icon: '📅', access: 'content' },
      { id: 'ai-assistant', label: 'AI Assistant', icon: '🤖', access: 'content' }
    )
  }

  // Review sections - only visible to analysts, PMs, and admins
  if (canReviewDocuments) {
    sections.push(
      { id: 'documents-pending-approval', label: 'Documents Pending Approval', icon: '✅', access: 'review', isExternalLink: true }
    )
  }

  // Management sections - only visible to PM/Admin
  // Note: Project Access management moved to project list for better UX
  // if (canManageAccess) {
  //   sections.push({ id: 'project-access', label: 'Project Access', icon: '⚙️', access: 'management' })
  // }

  return (
    <div className="w-64 bg-white shadow-md rounded-lg p-4">
      <h3 
        className="text-lg font-semibold mb-4"
        style={{ color: theme.textColor }}
      >
        Project Sections
      </h3>
      
      <nav className="space-y-2">
        {sections.map((section) => {
          const isExternalLink = (section as any).isExternalLink;
          
          if (isExternalLink) {
            return (
              <button
                key={section.id}
                onClick={() => router.push(`/projects/${projectId}/documents-pending-approval`)}
                className="w-full text-left px-4 py-3 rounded-md transition-colors hover:bg-gray-50"
                style={{ color: theme.textColor }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{section.icon}</span>
                  <span className="font-medium">{section.label}</span>
                </div>
              </button>
            );
          }
          
          return (
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
          );
        })}
      </nav>

      {/* Access level indicator */}
      {!hasContentAccess && canManageAccess && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-yellow-800 text-sm">
            You can manage this project but don't have access to its content. 
            Add yourself to a group to view documents and other features.
          </p>
        </div>
      )}
    </div>
  )
} 