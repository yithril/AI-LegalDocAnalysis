'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/components/providers/ThemeProvider'
import { useApiClient } from '@/lib/api-client'
import DocumentUploadModal from '@/components/documents/DocumentUploadModal'

interface ProjectDocumentsProps {
  projectId: number;
}

export default function ProjectDocuments({ projectId }: ProjectDocumentsProps) {
  const { theme } = useTheme()
  const { user, isAnalyst, isPM, isAdmin } = useAuth()
  const apiClient = useApiClient()
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [canUpload, setCanUpload] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  // Memoized access check to prevent re-renders
  const checkProjectAccess = useCallback(async () => {
    if (canUpload !== null) return // Already checked
    
    try {
      setLoading(true)
      // Try to get project details - if successful, user has access
      await apiClient.getProject(projectId)
      setCanUpload(true)
    } catch (error) {
      console.error('Error uploading document:', error);
      setCanUpload(false)
    } finally {
      setLoading(false)
    }
  }, [projectId, apiClient, canUpload])

  // Check access only once when component mounts or projectId changes
  useEffect(() => {
    if (projectId) {
      checkProjectAccess()
    }
  }, [projectId, checkProjectAccess])

  const handleUploadSuccess = () => {
    // TODO: Refresh document list
    setIsUploadModalOpen(false);
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2
            className="text-xl font-semibold"
            style={{ color: theme.textColor }}
          >
            Documents
          </h2>
          {canUpload === true && (
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Upload Document</span>
            </button>
          )}
        </div>
        
        <div className="space-y-4">
          <p
            className="text-sm"
            style={{ color: theme.secondaryColor }}
          >
            Document management coming soon...
          </p>
          <p className="text-sm" style={{ color: theme.secondaryColor }}>
            Upload and analyze legal documents, contracts, and other project-related files.
          </p>
          
          {canUpload === false && (
            <div className="p-4 border border-gray-300 rounded-lg">
              <p className="text-gray-500 text-center">
                You need to be a member of a group assigned to this project to upload documents.
              </p>
            </div>
          )}
        </div>
      </div>

      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={handleUploadSuccess}
        projectId={projectId}
      />
    </div>
  )
} 