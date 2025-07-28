'use client';

import { useSession } from '@auth0/nextjs-auth0/client';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { isAdmin, isProjectManager, isAnalyst, isViewer } from '../../lib/auth-utils';
import SimpleLayout from './SimpleLayout';
import AdminLayout from './AdminLayout';
import ProjectsList from '../projects/ProjectsList';
import UserGroupsList from '../user-groups/UserGroupsList';
import NotificationsBox from './NotificationsBox';

export default function RoleBasedDashboard() {
  const { data: session, isLoading } = useSession();
  const router = useRouter();

  // Wait for session to load
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If no session, redirect to login (this should be handled by middleware, but just in case)
  if (!session) {
    router.push('/auth/login');
    return null;
  }

  const userRoles = session.user?.['https://your-app.com/roles'] || [];

  // Determine user's highest role for dashboard selection
  const isUserAdmin = isAdmin(userRoles);
  const isUserPM = isProjectManager(userRoles);
  const isUserAnalyst = isAnalyst(userRoles);
  const isUserViewer = isViewer(userRoles);

  // Event handlers for projects
  const handleViewProject = (project) => {
    console.log('View project clicked:', project);
    // TODO: Navigate to project documents view
  };

  const handleManageGroups = (project) => {
    console.log('Manage groups clicked:', project);
    // TODO: Open group management modal
  };

  const handleAIAssistant = (project) => {
    console.log('AI Assistant clicked:', project);
    // TODO: Navigate to AI chat interface
  };

  const handleCreateProject = () => {
    console.log('Create project clicked');
    // TODO: Open create project modal
  };

  // Event handlers for user groups
  const handleViewGroup = (group) => {
    console.log('View group clicked:', group);
    // TODO: Navigate to group details view
  };

  const handleCreateGroup = () => {
    console.log('Create group clicked');
    // TODO: Open create group modal
  };

  const handleEditGroup = (group) => {
    console.log('Edit group clicked:', group);
    // TODO: Open edit group modal
  };

  const handleDeleteGroup = (group) => {
    console.log('Delete group clicked:', group);
    // TODO: Open delete confirmation modal
  };

  const handleManageUsers = (group) => {
    console.log('Manage users clicked:', group);
    // TODO: Open user management modal
  };

  // Admin Dashboard - Full access with sidebar and user groups
  if (isUserAdmin) {
    const sidebarContent = (
      <ProjectsList 
        onViewProject={handleViewProject}
        onManageGroups={handleManageGroups}
        onAIAssistant={handleAIAssistant}
        onCreateProject={handleCreateProject}
      />
    );

    const mainContent = (
      <div className="flex gap-6 h-full">
        <div className="flex-1">
          <UserGroupsList 
            onViewGroup={handleViewGroup}
            onCreateGroup={handleCreateGroup}
            onEditGroup={handleEditGroup}
            onDeleteGroup={handleDeleteGroup}
            onManageUsers={handleManageUsers}
          />
        </div>
        
        <div className="w-96">
          <NotificationsBox />
        </div>
      </div>
    );

    return (
      <AdminLayout 
        sidebarContent={sidebarContent}
        title="Admin Dashboard"
        subtitle="Manage projects and user groups"
      >
        {mainContent}
      </AdminLayout>
    );
  }

  // Project Manager Dashboard - Similar to admin but no delete permissions
  if (isUserPM) {
    const sidebarContent = (
      <ProjectsList 
        onViewProject={handleViewProject}
        onManageGroups={handleManageGroups}
        onAIAssistant={handleAIAssistant}
        onCreateProject={handleCreateProject}
      />
    );

    const mainContent = (
      <div className="flex gap-6 h-full">
        <div className="flex-1">
          <UserGroupsList 
            onViewGroup={handleViewGroup}
            onCreateGroup={handleCreateGroup}
            onEditGroup={handleEditGroup}
            onDeleteGroup={handleDeleteGroup}
            onManageUsers={handleManageUsers}
          />
        </div>
        
        <div className="w-96">
          <NotificationsBox />
        </div>
      </div>
    );

    return (
      <AdminLayout 
        sidebarContent={sidebarContent}
        title="Project Manager Dashboard"
        subtitle="Manage projects and user groups"
      >
        {mainContent}
      </AdminLayout>
    );
  }

  // Analyst/Viewer Dashboard - Simple layout with just projects
  if (isUserAnalyst || isUserViewer) {
    return (
      <SimpleLayout 
        title="Projects" 
        subtitle="Select a project to view documents"
      >
        <ProjectsList 
          onViewProject={handleViewProject}
          onAIAssistant={handleAIAssistant}
        />
      </SimpleLayout>
    );
  }

  // Fallback - Simple layout for unknown roles
  return (
    <SimpleLayout 
      title="Dashboard" 
      subtitle="Welcome to the application"
    >
      <div className="text-center py-8">
        <p className="text-gray-500">Welcome! Your role permissions are being configured.</p>
      </div>
    </SimpleLayout>
  );
} 