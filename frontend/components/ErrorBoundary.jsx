'use client';

import React from 'react';
import logger from '../lib/logger';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    logger.error('React Error Boundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack
    });

    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="error-boundary">
          <div className="container mt-5">
            <div className="row justify-content-center">
              <div className="col-md-8 text-center">
                <h1 className="display-4 text-danger mb-4">
                  <i className="fas fa-exclamation-triangle"></i>
                  Oops! Something went wrong
                </h1>
                <p className="lead mb-4">
                  We're sorry, but something unexpected happened. 
                  Our team has been notified and we're working to fix it.
                </p>
                <div className="mb-4">
                  <button 
                    className="btn btn-primary me-3"
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo"></i> Reload Page
                  </button>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => window.location.href = '/'}
                  >
                    <i className="fas fa-home"></i> Go Home
                  </button>
                </div>
                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="mt-4 text-start">
                    <summary className="text-danger cursor-pointer">
                      Error Details (Development Only)
                    </summary>
                    <pre className="bg-light p-3 mt-2 rounded text-danger small">
                      {this.state.error.toString()}
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 