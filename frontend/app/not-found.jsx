'use client';

import React from 'react';
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="not-found-page">
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-8 text-center">
            <div className="error-page">
              <h1 className="display-1 text-muted mb-4">404</h1>
              <h2 className="display-6 mb-4">Page Not Found</h2>
              <p className="lead mb-4">
                The page you're looking for doesn't exist or has been moved.
              </p>
              <div className="mb-4">
                <Link href="/" className="btn btn-primary me-3">
                  <i className="fas fa-home"></i> Go Home
                </Link>
                <button 
                  className="btn btn-outline-secondary"
                  onClick={() => window.history.back()}
                >
                  <i className="fas fa-arrow-left"></i> Go Back
                </button>
              </div>
              <div className="mt-5">
                <h5 className="mb-3">Popular Pages</h5>
                <div className="row justify-content-center">
                  <div className="col-md-6">
                    <div className="list-group">
                      <Link href="/" className="list-group-item list-group-item-action">
                        <i className="fas fa-home me-2"></i>
                        Home
                      </Link>
                      <Link href="/projects" className="list-group-item list-group-item-action">
                        <i className="fas fa-folder me-2"></i>
                        Projects
                      </Link>
                      <Link href="/documents" className="list-group-item list-group-item-action">
                        <i className="fas fa-file-alt me-2"></i>
                        Documents
                      </Link>
                      <Link href="/profile" className="list-group-item list-group-item-action">
                        <i className="fas fa-user me-2"></i>
                        Profile
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 