'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { UserRole, isPM, isAdmin } from '@/lib/roles'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch'
import CreateProjectModal from './projects/CreateProjectModal'
import EditProjectModal from './projects/EditProjectModal'

// Types
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

interface ProjectListProps {
  className?: string
}

// Helper functions for role-based UI visibility
export const canCreateProject = (userRole: string): boolean => {
  return isPM(userRole) || isAdmin(userRole)
}

export const canEditProject = (userRole: string): boolean => {
  return isPM(userRole) || isAdmin(userRole)
}

export const canManageGroups = (userRole: string): boolean => {
  return isPM(userRole) || isAdmin(userRole)
}

export const canDeleteProject = (userRole: string): boolean => {
  return isPM(userRole) || isAdmin(userRole)
}

export default function ProjectList({ className = '' }: ProjectListProps) {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  
  const { user, userRole } = useAuth()
  const { theme } = useTheme()
  const { authenticatedFetch, hasToken } = useAuthenticatedFetch({
    onError: (error) => setError(error)
  })

  useEffect(() => {
    if (hasToken) {
      fetchProjects()
    }
  }, [hasToken])

  const fetchProjects = async () => {
    try {
      setIsLoading(true)
      const response = await authenticatedFetch('/api/projects/')
      const data = await response.json()
      setProjects(data)
    } catch (err) {
      console.error('ProjectList: Error in fetchProjects:', err)
      setError('Failed to load projects')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project?')) {
      return
    }

    try {
      await authenticatedFetch(`/api/projects/${projectId}`, {
        method: 'DELETE',
      })

      // Refresh the project list
      fetchProjects()
    } catch (err) {
      setError('Failed to delete project')
      console.error('Error deleting project:', err)
    }
  }

  const handleCreateSuccess = () => {
    fetchProjects()
  }

  const handleEditSuccess = () => {
    fetchProjects()
  }

  const handleEditProject = (project: Project) => {
    setSelectedProject(project)
    setIsEditModalOpen(true)
  }

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false)
    setSelectedProject(null)
  }

  const handleOpenProject = (projectId: number) => {
    router.push(`/projects/${projectId}`)
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
          onClick={fetchProjects}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className={`${className}`}>
      {/* Header with Create Button */}
      <div className="flex justify-between items-center mb-6">
        <h2 
          className="text-2xl font-bold"
          style={{ color: theme.textColor }}
        >
          Projects
        </h2>
        
        {canCreateProject(userRole) && (
          <button
            className="px-4 py-2 text-white rounded-md hover:opacity-90 transition-opacity"
            style={{ backgroundColor: theme.accentColor }}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create Project
          </button>
        )}
      </div>

      {/* Projects Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200 rounded-lg">
          <thead>
            <tr style={{ backgroundColor: theme.backgroundColor }}>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                <span style={{ color: theme.textColor }}>Name</span>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                <span style={{ color: theme.textColor }}>Description</span>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                <span style={{ color: theme.textColor }}>Start Date</span>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                <span style={{ color: theme.textColor }}>End Date</span>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                <span style={{ color: theme.textColor }}>Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {projects.map((project, index) => (
              <tr 
                key={project.id}
                className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium" style={{ color: theme.textColor }}>
                    {project.name}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm" style={{ color: theme.secondaryColor }}>
                    {project.description || 'No description'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm" style={{ color: theme.secondaryColor }}>
                    {formatDate(project.document_start_date)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm" style={{ color: theme.secondaryColor }}>
                    {formatDate(project.document_end_date)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    {/* Open Button */}
                    <button
                      className="text-blue-600 hover:text-blue-900"
                      onClick={() => handleOpenProject(project.id)}
                    >
                      Open
                    </button>

                    {/* Edit Button */}
                    {canEditProject(userRole) && (
                      <button
                        className="text-green-600 hover:text-green-900"
                        onClick={() => handleEditProject(project)}
                      >
                        Edit
                      </button>
                    )}

                    {/* Manage Groups Button */}
                    {canManageGroups(userRole) && (
                      <button
                        className="text-purple-600 hover:text-purple-900"
                        onClick={() => {/* TODO: Navigate to manage groups */}}
                      >
                        Groups
                      </button>
                    )}

                    {/* Delete Button */}
                    {canDeleteProject(userRole) && (
                      <button
                        className="text-red-600 hover:text-red-900"
                        onClick={() => handleDeleteProject(project.id)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {projects.length === 0 && (
          <div className="text-center py-8">
            <p style={{ color: theme.secondaryColor }}>
              No projects found. {canCreateProject(userRole) && 'Create your first project to get started.'}
            </p>
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleCreateSuccess}
      />

      {/* Edit Project Modal */}
      <EditProjectModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        project={selectedProject}
        onSuccess={handleEditSuccess}
      />
    </div>
  )
} 