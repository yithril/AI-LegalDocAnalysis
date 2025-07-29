'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

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

interface ProjectOverviewProps {
  project: Project
}

export default function ProjectOverview({ project }: ProjectOverviewProps) {
  const { theme } = useTheme()

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="space-y-6">
      {/* Project Info Card */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2
          className="text-xl font-semibold mb-4"
          style={{ color: theme.textColor }}
        >
          Project Information
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Description
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {project.description || 'No description provided'}
            </p>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Date Range
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {formatDate(project.document_start_date)} - {formatDate(project.document_end_date)}
            </p>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Created
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {formatDate(project.created_at)}
              {project.created_by && ` by ${project.created_by}`}
            </p>
          </div>

          <div>
            <h3
              className="text-sm font-medium mb-2"
              style={{ color: theme.textColor }}
            >
              Last Updated
            </h3>
            <p
              className="text-sm"
              style={{ color: theme.secondaryColor }}
            >
              {formatDate(project.updated_at)}
              {project.updated_by && ` by ${project.updated_by}`}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3
            className="text-lg font-semibold mb-2"
            style={{ color: theme.textColor }}
          >
            Documents
          </h3>
          <p
            className="text-2xl font-bold"
            style={{ color: theme.accentColor }}
          >
            0
          </p>
          <p className="text-sm" style={{ color: theme.secondaryColor }}>
            No documents uploaded yet
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3
            className="text-lg font-semibold mb-2"
            style={{ color: theme.textColor }}
          >
            Actors
          </h3>
          <p
            className="text-2xl font-bold"
            style={{ color: theme.accentColor }}
          >
            0
          </p>
          <p className="text-sm" style={{ color: theme.secondaryColor }}>
            No actors identified yet
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3
            className="text-lg font-semibold mb-2"
            style={{ color: theme.textColor }}
          >
            Timeline Events
          </h3>
          <p
            className="text-2xl font-bold"
            style={{ color: theme.accentColor }}
          >
            0
          </p>
          <p className="text-sm" style={{ color: theme.secondaryColor }}>
            No timeline events yet
          </p>
        </div>
      </div>
    </div>
  )
} 