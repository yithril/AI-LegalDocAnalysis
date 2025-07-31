import React, { useState, useEffect } from 'react';
import CSVViewer from './CSVViewer';

interface DocumentViewerProps {
  document: {
    filename: string;
    original_file_path: string;
    text_extraction_result?: string;
    file_size?: number; // File size in bytes
  };
  className?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document, className = '' }) => {
  const [isLoading, setIsLoading] = useState(true);
  const fileType = document.filename.split('.').pop()?.toLowerCase();
  
  // Check file size (50MB threshold)
  const isLargeFile = document.file_size && document.file_size > 50 * 1024 * 1024;
  
  // For text documents, stop loading immediately
  useEffect(() => {
    if (!['pdf', 'docx', 'xlsx', 'xls', 'pptx', 'doc'].includes(fileType || '')) {
      setIsLoading(false);
    }
  }, [fileType]);
  
  // PDF Viewer
  if (fileType === 'pdf') {
    return (
      <div className={`document-viewer ${className}`}>
        {isLargeFile && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-yellow-800 text-sm">
              ⚠️ Large file detected. Loading may take time...
            </p>
          </div>
        )}
        
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600">Loading document...</p>
              {isLargeFile && (
                <p className="text-sm text-gray-500 mt-1">Large files may take longer</p>
              )}
            </div>
          </div>
        )}
        
        <iframe
          src={document.original_file_path}
          className="w-full h-full min-h-[600px] border border-gray-200 rounded"
          title={`PDF Viewer - ${document.filename}`}
          onLoad={() => setIsLoading(false)}
          style={{ display: isLoading ? 'none' : 'block' }}
        />
      </div>
    );
  }
  
  // Office Documents (DOCX, XLSX, XLS, PPTX, DOC)
  if (['docx', 'xlsx', 'xls', 'pptx', 'doc'].includes(fileType || '')) {
    const officeViewerUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(document.original_file_path)}`;
    
    return (
      <div className={`document-viewer ${className}`}>
        {isLargeFile && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-yellow-800 text-sm">
              ⚠️ Large file detected. Loading may take time...
            </p>
          </div>
        )}
        
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600">Loading document...</p>
              {isLargeFile && (
                <p className="text-sm text-gray-500 mt-1">Large files may take longer</p>
              )}
            </div>
          </div>
        )}
        
        <iframe
          src={officeViewerUrl}
          className="w-full h-full min-h-[600px] border border-gray-200 rounded"
          title={`Office Viewer - ${document.filename}`}
          onLoad={() => setIsLoading(false)}
          style={{ display: isLoading ? 'none' : 'block' }}
        />
      </div>
    );
  }
  
  // CSV Viewer
  if (fileType === 'csv') {
    return (
      <div className={`document-viewer ${className}`}>
        {isLargeFile && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-yellow-800 text-sm">
              ⚠️ Large file detected. Loading may take time...
            </p>
          </div>
        )}
        
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600">Loading CSV...</p>
              {isLargeFile && (
                <p className="text-sm text-gray-500 mt-1">Large files may take longer</p>
              )}
            </div>
          </div>
        )}
        
        <div className="w-full h-full min-h-[600px] border border-gray-200 rounded bg-white overflow-auto">
          <CSVViewer 
            content={document.text_extraction_result || ''} 
            onLoad={() => setIsLoading(false)}
            style={{ display: isLoading ? 'none' : 'block' }}
          />
        </div>
      </div>
    );
  }
  
  // Text-based documents or fallback
  return (
    <div className={`document-viewer ${className}`}>
      {document.text_extraction_result ? (
        <div className="w-full h-full min-h-[600px] border border-gray-200 rounded bg-white p-4 overflow-auto">
          <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800">
            {document.text_extraction_result}
          </pre>
        </div>
      ) : (
        <div className="w-full h-full min-h-[600px] border border-gray-200 rounded bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-500 mb-2">Unable to display this file type</p>
            <a
              href={document.original_file_path}
              download={document.filename}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Download original file
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer; 