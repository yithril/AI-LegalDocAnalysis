'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { useSession } from 'next-auth/react';
import DocumentReview from '@/components/documents/DocumentReview';

export default function DocumentsPendingApprovalPage() {
  const params = useParams();
  const { data: session } = useSession();
  
  const projectId = parseInt(params.id as string);
  const userRole = session?.user?.role || 'viewer';

  return (
    <div className="h-full">
      <DocumentReview 
        projectId={projectId} 
        userRole={userRole} 
      />
    </div>
  );
} 