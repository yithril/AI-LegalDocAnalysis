'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch'
import ProjectSidebar from '@/components/projects/ProjectSidebar'
import ProjectOverview from '@/components/projects/sections/ProjectOverview'
import ProjectDocuments from '@/components/projects/sections/ProjectDocuments'
import ProjectActors from '@/components/projects/sections/ProjectActors'
import ProjectTimeline from '@/components/projects/sections/ProjectTimeline'
import ProjectAIAssistant from '@/components/projects/sections/ProjectAIAssistant'
import ProjectAccess from '@/components/projects/ProjectAccess'

interface Project {
  id: number
  name: string
  description?: string
  document_start_date: string
  document_end_date: string
  tenant_id: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
}

export default function ProjectDashboard() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const { theme } = useTheme()
  const { authenticatedFetch } = useAuthenticatedFetch()
  
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeSection, setActiveSection] = useState('overview')

  const projectId = params.id as string

  useEffect(() => {
    if (projectId) {
      fetchProject()
    }
  }, [projectId])

  const fetchProject = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await authenticatedFetch(`/api/projects/${projectId}`)
      const data = await response.json()
      setProject(data)
    } catch (err) {
      setError('Failed to load project')
      console.error('Error fetching project:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const renderActiveSection = () => {
    if (!project) return null

    switch (activeSection) {
      case 'overview':
        return <ProjectOverview project={project} />
      case 'documents':
        return <ProjectDocuments />
      case 'actors':
        return <ProjectActors />
      case 'timeline':
        return <ProjectTimeline />
      case 'ai-assistant':
        return <ProjectAIAssistant />
      case 'project-access':
        return <ProjectAccess projectId={project.id} />
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
        />

        {/* Main Content */}
        <div className="flex-1">
          {renderActiveSection()}
        </div>
      </div>
    </div>
  )
} 