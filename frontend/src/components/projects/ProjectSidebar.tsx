'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useApiClient } from '@/lib/api-client'

interface ProjectSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
  projectId: number
}

export default function ProjectSidebar({ activeSection, onSectionChange, projectId }: ProjectSidebarProps) {
  const { isPM, isAdmin, isAnalyst } = useAuth()
  const { theme } = useTheme()
  const apiClient = useApiClient()
  
  const [hasContentAccess, setHasContentAccess] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  const canManageAccess = isPM() || isAdmin()
  const canReviewDocuments = isPM() || isAdmin() || isAnalyst()

  // Memoized access check to prevent re-renders
  const checkContentAccess = useCallback(async () => {
    if (hasContentAccess !== null) return // Already checked
    
    try {
      setLoading(true)
      // Try to get project details - if successful, user has content access
      await apiClient.getProject(projectId)
      setHasContentAccess(true)
    } catch (error) {
      console.error('Error checking project access:', error);
      setHasContentAccess(false)
    } finally {
      setLoading(false)
    }
  }, [projectId, apiClient, hasContentAccess])

  // Check access only once when component mounts or projectId changes
  useEffect(() => {
    if (projectId) {
      checkContentAccess()
    }
  }, [projectId, checkContentAccess])

  // Always show Overview (general project info)
  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊', access: 'always' }
  ]

  // Content sections - only visible to group members
  if (hasContentAccess === true) {
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
      { id: 'documents-pending-approval', label: 'Documents Pending Approval', icon: '✅', access: 'review' }
    )
  }

  // Management sections - only visible to PM/Admin
  // Note: Project Access management moved to project list for better UX
  // if (canManageAccess) {
  //   sections.push({ id: 'project-access', label: 'Project Access', icon: '⚙️', access: 'management' })
  // }

  if (loading) {
    return (
      <div className="w-64 bg-white shadow-md rounded-lg p-4">
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
        </div>
      </div>
    )
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

      {/* Access level indicator */}
      {hasContentAccess === false && canManageAccess && (
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