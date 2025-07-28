'use client';

import React from 'react';
import logger from '../lib/logger';

export default function Error({ error, reset }) {
  React.useEffect(() => {
    // Log the error
    logger.error('Global error caught:', {
      message: error.message,
      stack: error.stack
    });
  }, [error]);

  return (
    <div className="global-error-page">
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-8 text-center">
            <div className="error-page">
              <h1 className="display-4 text-danger mb-4">
                <i className="fas fa-exclamation-triangle"></i>
                Something went wrong!
              </h1>
              <p className="lead mb-4">
                We encountered an unexpected error. Please try again.
              </p>
              <div className="mb-4">
                <button 
                  className="btn btn-primary me-3"
                  onClick={() => reset()}
                >
                  <i className="fas fa-redo"></i> Try Again
                </button>
                <button 
                  className="btn btn-outline-secondary"
                  onClick={() => window.location.href = '/'}
                >
                  <i className="fas fa-home"></i> Go Home
                </button>
              </div>
              {process.env.NODE_ENV === 'development' && (
                <details className="mt-4 text-start">
                  <summary className="text-danger cursor-pointer">
                    Error Details (Development Only)
                  </summary>
                  <pre className="bg-light p-3 mt-2 rounded text-danger small">
                    {error.message}
                    {error.stack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 