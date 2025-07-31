import React, { useState, useEffect } from 'react';
import DocumentViewer from './DocumentViewer';
import { useApiClient } from '@/lib/api-client';
import type { GetDocumentResponse } from '@/types/api';

// Use the API type instead of custom interface
type Document = GetDocumentResponse;

interface DocumentReviewProps {
  projectId: number;
  userRole: string; // 'viewer' | 'analyst' | 'pm' | 'admin'
}

const DocumentReview: React.FC<DocumentReviewProps> = ({ projectId, userRole }) => {
  const apiClient = useApiClient();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [humanSummary, setHumanSummary] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Check if user has access to review documents
  const canReview = ['analyst', 'pm', 'admin'].includes(userRole);
  
  if (!canReview) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Access Denied</h2>
          <p className="text-gray-500">You don't have permission to review documents.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  useEffect(() => {
    if (documents.length > 0 && currentIndex < documents.length) {
      const currentDoc = documents[currentIndex];
      setHumanSummary(currentDoc.human_summary || '');
    }
  }, [currentIndex, documents]);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getDocumentsReadyForReview(projectId);
      setDocuments(response.items || []);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccept = async () => {
    if (currentIndex >= documents.length) return;
    
    setIsSubmitting(true);
    try {
      const currentDoc = documents[currentIndex];
      await apiClient.updateDocument(currentDoc.id, {
        status: 'HUMAN_REVIEW_APPROVED',
        human_summary: humanSummary
      });
      
      // Move to next document
      if (currentIndex < documents.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        // No more documents
        setDocuments([]);
        setCurrentIndex(0);
      }
    } catch (error) {
      console.error('Error accepting document:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (currentIndex >= documents.length) return;
    
    setIsSubmitting(true);
    try {
      const currentDoc = documents[currentIndex];
      await apiClient.updateDocument(currentDoc.id, {
        status: 'HUMAN_REVIEW_REJECTED',
        human_summary: humanSummary
      });
      
      // Move to next document
      if (currentIndex < documents.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        // No more documents
        setDocuments([]);
        setCurrentIndex(0);
      }
    } catch (error) {
      console.error('Error rejecting document:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < documents.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading documents...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">🎉 All Done!</h2>
          <p className="text-gray-500 mb-4">No documents need review</p>
          <button 
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Project List
          </button>
        </div>
      </div>
    );
  }

  const currentDocument = documents[currentIndex];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Document Review</h1>
            <p className="text-sm text-gray-500">
              Document {currentIndex + 1} of {documents.length}
            </p>
          </div>
          <div className="text-sm text-gray-500">
            {currentDocument.filename}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Document Viewer */}
        <div className="flex-1 border-r border-gray-200">
          <DocumentViewer document={currentDocument} className="h-full" />
        </div>

        {/* Right Panel - Summary & Actions */}
        <div className="w-96 bg-white p-6 flex flex-col">
          {/* Document Info */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Document Information</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium text-gray-700">Type:</span>
                <span className="ml-2 text-gray-600">
                  {currentDocument.document_type || 'Unknown'}
                </span>
              </div>
              {currentDocument.classification_confidence && (
                <div>
                  <span className="font-medium text-gray-700">Confidence:</span>
                  <span className="ml-2 text-gray-600">
                    {(currentDocument.classification_confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* AI Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI Summary</h3>
            <div className="bg-gray-50 p-3 rounded border text-sm text-gray-700">
              {currentDocument.classification_summary || 'No AI summary available'}
            </div>
          </div>

          {/* Human Summary */}
          <div className="mb-6 flex-1">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Human Summary</h3>
            <textarea
              value={humanSummary}
              onChange={(e) => setHumanSummary(e.target.value)}
              placeholder="Add your summary or notes here..."
              className="w-full h-32 p-3 border border-gray-300 rounded resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Navigation & Actions */}
          <div className="space-y-3">
            {/* Navigation */}
            <div className="flex justify-between">
              <button
                onClick={handlePrevious}
                disabled={currentIndex === 0 || isSubmitting}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={handleNext}
                disabled={currentIndex === documents.length - 1 || isSubmitting}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleReject}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Processing...' : 'Reject'}
              </button>
              <button
                onClick={handleAccept}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Processing...' : 'Accept'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentReview; 