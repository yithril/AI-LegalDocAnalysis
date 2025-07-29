'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch';
import DocumentUpload from './DocumentUpload';
import { getStatusColor, getStatusText } from '@/lib/documentStatus';

interface Document {
  id: number;
  filename: string;
  original_file_path: string;
  project_id: number;
  status: string;
  tenant_id: number;
  created_at: string;
  created_by?: string;
  updated_at: string;
  updated_by?: string;
}

interface DocumentListProps {
  projectId: number;
  statusFilter?: string; // Optional status filter for human review workflow
}

export default function DocumentList({ projectId, statusFilter }: DocumentListProps) {
  const { user, isAnalyst, isPM, isAdmin } = useAuth();
  const { theme } = useTheme();
  const { authenticatedFetch, hasToken } = useAuthenticatedFetch({
    onError: (error) => setError(error)
  });
  
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    if (hasToken) {
      fetchDocuments();
    }
  }, [hasToken, projectId, statusFilter]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Build URL with optional status filter
      let url = `/api/documents/project/${projectId}`;
      if (statusFilter) {
        url += `?status=${encodeURIComponent(statusFilter)}`;
      }
      
      const response = await authenticatedFetch(url);
      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (document: Document) => {
    // Add the new document to the list
    setDocuments(prev => [document, ...prev]);
    setShowUpload(false);
  };

  const handleUploadError = (error: string) => {
    setError(error);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };



  const canUpload = isAnalyst() || isPM() || isAdmin();

  if (loading) {
    return (
      <div className="p-6">
        <p style={{ color: theme.textColor }}>Loading documents...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 
          className="text-2xl font-bold"
          style={{ color: theme.textColor }}
        >
          Project Documents
        </h2>
        {canUpload && (
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="px-4 py-2 text-white rounded-md hover:opacity-90 transition-opacity"
            style={{ backgroundColor: theme.accentColor }}
          >
            {showUpload ? 'Cancel Upload' : '+ Upload Document'}
          </button>
        )}
      </div>

      {/* Upload Section */}
      {showUpload && canUpload && (
        <div className="border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Upload New Document</h3>
          <DocumentUpload
            projectId={projectId}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
          <button 
            onClick={fetchDocuments}
            className="mt-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded text-sm"
          >
            Retry
          </button>
        </div>
      )}

      {/* Documents Table */}
      {documents.length === 0 ? (
        <div className="text-center py-8">
          <p style={{ color: theme.secondaryColor }}>No documents found for this project.</p>
          {canUpload && (
            <p className="mt-2 text-sm" style={{ color: theme.secondaryColor }}>
              Upload your first document to get started.
            </p>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 rounded-lg">
            <thead>
              <tr style={{ backgroundColor: theme.backgroundColor }}>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Document</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Status</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Uploaded</span>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Updated</span>
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider border-b">
                  <span style={{ color: theme.textColor }}>Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {documents.map((document, index) => (
                <tr 
                  key={document.id} 
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium" style={{ color: theme.textColor }}>
                      {document.filename}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(document.status)}`}>
                      {getStatusText(document.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {formatDate(document.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm" style={{ color: theme.secondaryColor }}>
                      {formatDate(document.updated_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => {/* TODO: View document */}}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </button>
                      {(isPM() || isAdmin()) && (
                        <button
                          onClick={() => {/* TODO: Delete document */}}
                          className="text-red-600 hover:text-red-900"
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
        </div>
      )}
    </div>
  );
} 