'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/components/providers/ThemeProvider';
import DocumentUpload from './DocumentUpload';
import type { CreateDocumentResponse } from '@/types/api';

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  projectId: number;
}

export default function DocumentUploadModal({ isOpen, onClose, onSuccess, projectId }: DocumentUploadModalProps) {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [error, setError] = useState<string | null>(null);

  const handleUploadSuccess = (document: CreateDocumentResponse) => {
    console.log('Document uploaded successfully:', document);
    onSuccess();
    onClose();
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 
              className="text-xl font-semibold"
              style={{ color: theme.textColor }}
            >
              Upload Document
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              <p>Upload a document to this project. The document will be processed and analyzed automatically.</p>
            </div>

            <DocumentUpload
              projectId={projectId}
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />

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
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 