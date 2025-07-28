'use client';

import { 
  VStack, 
  HStack, 
  Box, 
  Text, 
  Button, 
  useColorModeValue,
  Heading,
  Flex,
  Badge,
  Icon,
  useDisclosure,
  Spinner,
  Alert,
  AlertIcon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer
} from '@chakra-ui/react';
import { AddIcon, ViewIcon, SettingsIcon, ChatIcon } from '@chakra-ui/icons';
import { useSession } from '@auth0/nextjs-auth0/client';
import { canCreateProjects, isProjectManager } from '../../lib/auth-utils';
import { useProjects } from '../../hooks/useProjects';

export default function ProjectsList({ onProjectClick, onCreateProject, onViewProject, onManageGroups, onAIAssistant }) {
  const { data: session } = useSession();
  const userRoles = session?.user?.['https://your-app.com/roles'] || [];
  const { projects, loading, error } = useProjects();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const handleCreateProject = () => {
    if (onCreateProject) {
      onCreateProject();
    }
  };

  const handleViewProject = (project) => {
    if (onViewProject) {
      onViewProject(project);
    }
  };

  const handleManageGroups = (project) => {
    if (onManageGroups) {
      onManageGroups(project);
    }
  };

  const handleAIAssistant = (project) => {
    if (onAIAssistant) {
      onAIAssistant(project);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <VStack spacing={4} align="stretch" h="full">
        <Flex justify="space-between" align="center">
          <Heading size="md">Projects</Heading>
          {canCreateProjects(userRoles) && (
            <Button
              size="sm"
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={handleCreateProject}
            >
              New Project
            </Button>
          )}
        </Flex>
        <Box flex={1} display="flex" alignItems="center" justifyContent="center">
          <Spinner size="lg" />
        </Box>
      </VStack>
    );
  }

  // Show error state
  if (error) {
    return (
      <VStack spacing={4} align="stretch" h="full">
        <Flex justify="space-between" align="center">
          <Heading size="md">Projects</Heading>
          {canCreateProjects(userRoles) && (
            <Button
              size="sm"
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={handleCreateProject}
            >
              New Project
            </Button>
          )}
        </Flex>
        <Alert status="error">
          <AlertIcon />
          Failed to load projects: {error}
        </Alert>
      </VStack>
    );
  }

  return (
    <VStack spacing={4} align="stretch" h="full">
      {/* Header with Create Button */}
      <Flex justify="space-between" align="center">
        <Heading size="md">Projects</Heading>
        {canCreateProjects(userRoles) && (
          <Button
            size="sm"
            leftIcon={<AddIcon />}
            colorScheme="blue"
            onClick={handleCreateProject}
          >
            New Project
          </Button>
        )}
      </Flex>

      {/* Projects Table */}
      <Box flex={1} overflowY="auto">
        {projects.length === 0 ? (
          // Empty State
          <Box 
            textAlign="center" 
            py={8}
            color={textColor}
          >
            <Text fontSize="lg" mb={2}>
              No projects currently
            </Text>
            <Text fontSize="sm">
              {canCreateProjects(userRoles) 
                ? "Click 'New Project' to create your first project"
                : "Contact your administrator to create projects"
              }
            </Text>
          </Box>
        ) : (
          // Projects Table
          <TableContainer>
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Project Name</Th>
                  <Th>Description</Th>
                  <Th>Status</Th>
                  <Th>Documents</Th>
                  <Th>Last Updated</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {projects.map((project) => (
                  <Tr key={project.id} _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}>
                    <Td fontWeight="medium">
                      {project.name}
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor} noOfLines={1}>
                        {project.description || 'No description'}
                      </Text>
                    </Td>
                    <Td>
                      <Badge 
                        size="sm" 
                        colorScheme={project.status === 'active' ? 'green' : 'gray'}
                      >
                        {project.status}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm">
                        {project.documentCount || 0}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor}>
                        {project.lastUpdated || 'recently'}
                      </Text>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Button
                          size="xs"
                          leftIcon={<ViewIcon />}
                          colorScheme="blue"
                          variant="outline"
                          onClick={() => handleViewProject(project)}
                        >
                          View
                        </Button>
                        
                        {isProjectManager(userRoles) && (
                          <Button
                            size="xs"
                            leftIcon={<SettingsIcon />}
                            colorScheme="orange"
                            variant="outline"
                            onClick={() => handleManageGroups(project)}
                          >
                            Groups
                          </Button>
                        )}
                        
                        <Button
                          size="xs"
                          leftIcon={<ChatIcon />}
                          colorScheme="purple"
                          variant="outline"
                          onClick={() => handleAIAssistant(project)}
                        >
                          AI Assistant
                        </Button>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </VStack>
  );
} 