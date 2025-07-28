'use client';

import { Box, VStack, Heading, Text, Center, Flex } from '@chakra-ui/react';
import AdminLayout from '../../components/layouts/AdminLayout';
import NotificationsBox from '../../components/layouts/NotificationsBox';
import ProjectsList from '../../components/projects/ProjectsList';
import UserGroupsList from '../../components/user-groups/UserGroupsList';

export default function AdminDashboardPage() {
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

  // User Groups handlers
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

  // Projects list component
  const sidebarContent = (
    <ProjectsList 
      onViewProject={handleViewProject}
      onManageGroups={handleManageGroups}
      onAIAssistant={handleAIAssistant}
      onCreateProject={handleCreateProject}
    />
  );

  // Main content with user groups and notifications
  const mainContent = (
    <Flex gap={6} direction={{ base: 'column', lg: 'row' }} h="full">
      {/* Right Side - User Groups and Notifications Stacked */}
      <Box w={{ base: 'full', lg: '400px' }}>
        <VStack spacing={6} align="stretch" h="full">
          {/* User Groups Section */}
          <Box flex={1}>
            <UserGroupsList 
              onViewGroup={handleViewGroup}
              onCreateGroup={handleCreateGroup}
              onEditGroup={handleEditGroup}
              onDeleteGroup={handleDeleteGroup}
              onManageUsers={handleManageUsers}
            />
          </Box>
          
          {/* Notifications Section */}
          <Box flex={1}>
            <NotificationsBox />
          </Box>
        </VStack>
      </Box>
    </Flex>
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