'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useApiClient } from '@/lib/api-client'
import ProjectSidebar from '@/components/projects/ProjectSidebar'
import ProjectOverview from '@/components/projects/sections/ProjectOverview'
import ProjectDocuments from '@/components/projects/sections/ProjectDocuments'
import ProjectActors from '@/components/projects/sections/ProjectActors'
import ProjectTimeline from '@/components/projects/sections/ProjectTimeline'
import ProjectAIAssistant from '@/components/projects/sections/ProjectAIAssistant'
import ProjectAccess from '@/components/projects/ProjectAccess'
import type { GetProjectResponse } from '@/types/api'

export default function ProjectDashboard() {
  const params = useParams()
  const router = useRouter()
  const { user, isPM, isAdmin } = useAuth()
  const { theme } = useTheme()
  const apiClient = useApiClient()
  
  const [project, setProject] = useState<GetProjectResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeSection, setActiveSection] = useState('overview')
  const [hasContentAccess, setHasContentAccess] = useState(false)

  const projectId = params.id as string

  useEffect(() => {
    if (projectId) {
      fetchProject();
    }
  }, [projectId]);



  const fetchProject = async () => {
    try {
      setLoading(true);
      console.log('🔍 DEBUG: Fetching project with ID:', projectId);
      const data = await apiClient.getProject(projectId);
      console.log('🔍 DEBUG: Project data received:', data);
      console.log('🔍 DEBUG: can_access field:', data.can_access);
      console.log('🔍 DEBUG: User info:', { user, isPM: isPM(), isAdmin: isAdmin() });
      setProject(data);
      // Set content access based on the can_access field from the API
      setHasContentAccess(data.can_access);
      console.log('🔍 DEBUG: hasContentAccess set to:', data.can_access);
    } catch (error) {
      console.error('Error fetching project:', error);
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const renderActiveSection = () => {
    if (!project) return null

    // Content sections that require group membership
    const contentSections = ['documents', 'actors', 'timeline', 'ai-assistant']
    
    // Check if user is trying to access content without permission
    if (contentSections.includes(activeSection) && !hasContentAccess) {
      return (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-center py-8">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold mb-2" style={{ color: theme.textColor }}>
                Access Restricted
              </h3>
              <p className="text-gray-600 mb-4">
                You need to be a member of a group assigned to this project to access this section.
              </p>
              {(isPM() || isAdmin()) && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-blue-800 text-sm">
                    As a {isAdmin() ? 'Admin' : 'Project Manager'}, you can manage this project's groups 
                    in the "Project Access" section, but you need to be added to a group to view its content.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )
    }

    switch (activeSection) {
      case 'overview':
        return <ProjectOverview project={project} />
      case 'documents':
        return <ProjectDocuments projectId={project.id} />
      case 'actors':
        return <ProjectActors />
      case 'timeline':
        return <ProjectTimeline />
      case 'ai-assistant':
        return <ProjectAIAssistant />

      // Note: Project Access management moved to project list
      // case 'project-access':
      //   return <ProjectAccess projectId={project.id} />
      default:
        return <ProjectOverview project={project} />
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="p-6">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Project not found'}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Back to Projects
          </button>
        </div>
      </div>
    )
  }

    return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: theme.textColor }}
          >
            {project.name}
          </h1>
          <p
            className="text-lg"
            style={{ color: theme.secondaryColor }}
          >
            Project Dashboard
          </p>
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="px-4 py-2 text-white rounded-md hover:opacity-90 transition-opacity"
          style={{ backgroundColor: theme.accentColor }}
        >
          Back to Projects
        </button>
      </div>

      {/* Main Content with Sidebar */}
      <div className="flex gap-6">
        {/* Sidebar */}
        <ProjectSidebar
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          projectId={project.id}
          hasContentAccess={hasContentAccess}
        />

        {/* Main Content */}
        <div className="flex-1">
          {renderActiveSection()}
        </div>
      </div>
    </div>
  )
} 