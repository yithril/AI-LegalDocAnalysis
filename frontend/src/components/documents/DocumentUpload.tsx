'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import { useApiClient } from '@/lib/api-client';
import type { CreateDocumentResponse } from '@/types/api';

interface DocumentUploadProps {
  projectId: number;
  onUploadSuccess?: (document: CreateDocumentResponse) => void;
  onUploadError?: (error: string) => void;
}

// Backend supported file types (can extract text from these)
const ALLOWED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt', '.md'],
  'text/csv': ['.csv'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/rtf': ['.rtf']
};

const ALLOWED_EXTENSIONS = Object.values(ALLOWED_FILE_TYPES).flat();

export default function DocumentUpload({ projectId, onUploadSuccess, onUploadError }: DocumentUploadProps) {
  const { user, isAnalyst, isPM, isAdmin } = useAuth();
  const { theme } = useTheme();
  const apiClient = useApiClient();
  
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  // Check if user has permission to upload documents
  const canUpload = isAnalyst() || isPM() || isAdmin();

  const validateFile = (file: File): string | null => {
    // Check file size (not empty)
    if (file.size === 0) {
      return 'File cannot be empty';
    }

    // Check file extension
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      return `File type not supported. Allowed types: ${ALLOWED_EXTENSIONS.join(', ')}`;
    }

    // Check file size limit (set a reasonable limit like 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return 'File size too large. Maximum size is 50MB';
    }

    return null;
  };

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      onUploadError?.(validationError);
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      // Upload file using the typed API client
      const document = await apiClient.uploadDocument(projectId, file);
      setUploadProgress(100);

      onUploadSuccess?.(document);
      
      // Reset form
      setUploadProgress(0);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!canUpload) {
      setError('You do not have permission to upload documents');
      return;
    }

    if (acceptedFiles.length === 0) {
      setError('No valid files selected');
      return;
    }

    // Upload the first file (we could extend this to handle multiple files)
    uploadFile(acceptedFiles[0]);
  }, [canUpload, projectId]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ALLOWED_FILE_TYPES,
    multiple: false,
    disabled: uploading || !canUpload
  });

  if (!canUpload) {
    return (
      <div className="p-4 border border-gray-300 rounded-lg">
        <p className="text-gray-500 text-center">
          You need Analyst, Project Manager, or Admin permissions to upload documents.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : isDragReject 
              ? 'border-red-400 bg-red-50' 
              : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {/* Upload Icon */}
          <div className="text-4xl">
            {uploading ? '⏳' : isDragActive ? '📁' : '📤'}
          </div>
          
          {/* Upload Text */}
          <div>
            {uploading ? (
              <div className="space-y-2">
                <p className="text-lg font-medium">Uploading...</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500">{uploadProgress}%</p>
              </div>
            ) : isDragActive ? (
              <p className="text-lg font-medium text-blue-600">
                Drop the file here...
              </p>
            ) : (
              <div>
                <p className="text-lg font-medium mb-2">
                  Drag & drop a file here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Supported formats: PDF, DOCX, TXT, CSV, Excel, RTF, Markdown
                </p>
                <p className="text-sm text-gray-500">
                  Maximum size: 50MB
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* File Type Info */}
      <div className="text-xs text-gray-500">
        <p className="font-medium mb-1">Supported file types (text extraction):</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-1">
          <span>• PDF (.pdf)</span>
          <span>• Word (.docx)</span>
          <span>• Text (.txt, .md)</span>
          <span>• CSV (.csv)</span>
          <span>• Excel (.xlsx, .xls)</span>
          <span>• RTF (.rtf)</span>
        </div>
      </div>
    </div>
  );
} 