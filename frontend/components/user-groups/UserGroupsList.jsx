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
  TableContainer,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton
} from '@chakra-ui/react';
import { 
  AddIcon, 
  ViewIcon, 
  EditIcon, 
  DeleteIcon, 
  ChevronDownIcon,
  SettingsIcon
} from '@chakra-ui/icons';
import { useSession } from '@auth0/nextjs-auth0/client';
import { canManageUserGroups, isAdmin } from '../../lib/auth-utils';
import { useUserGroups } from '../../hooks/useUserGroups';

export default function UserGroupsList({ 
  onViewGroup, 
  onCreateGroup, 
  onEditGroup, 
  onDeleteGroup,
  onManageUsers 
}) {
  const { data: session } = useSession();
  const userRoles = session?.user?.['https://your-app.com/roles'] || [];
  const { userGroups, loading, error } = useUserGroups();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const handleCreateGroup = () => {
    if (onCreateGroup) {
      onCreateGroup();
    }
  };

  const handleViewGroup = (group) => {
    if (onViewGroup) {
      onViewGroup(group);
    }
  };

  const handleEditGroup = (group) => {
    if (onEditGroup) {
      onEditGroup(group);
    }
  };

  const handleDeleteGroup = (group) => {
    if (onDeleteGroup) {
      onDeleteGroup(group);
    }
  };

  const handleManageUsers = (group) => {
    if (onManageUsers) {
      onManageUsers(group);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <VStack spacing={4} align="stretch" h="full">
        <Flex justify="space-between" align="center">
          <Heading size="md">User Groups</Heading>
          {canManageUserGroups(userRoles) && (
            <Button
              size="sm"
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={handleCreateGroup}
            >
              New Group
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
          <Heading size="md">User Groups</Heading>
          {canManageUserGroups(userRoles) && (
            <Button
              size="sm"
              leftIcon={<AddIcon />}
              colorScheme="blue"
              onClick={handleCreateGroup}
            >
              New Group
            </Button>
          )}
        </Flex>
        <Alert status="error">
          <AlertIcon />
          Failed to load user groups: {error}
        </Alert>
      </VStack>
    );
  }

  return (
    <VStack spacing={4} align="stretch" h="full">
      {/* Header with Create Button */}
      <Flex justify="space-between" align="center">
        <Heading size="md">User Groups</Heading>
        {canManageUserGroups(userRoles) && (
          <Button
            size="sm"
            leftIcon={<AddIcon />}
            colorScheme="blue"
            onClick={handleCreateGroup}
          >
            New Group
          </Button>
        )}
      </Flex>

      {/* User Groups Table */}
      <Box flex={1} overflowY="auto">
        {userGroups.length === 0 ? (
          // Empty State
          <Box 
            textAlign="center" 
            py={8}
            color={textColor}
          >
            <Text fontSize="lg" mb={2}>
              No user groups currently
            </Text>
            <Text fontSize="sm">
              {canManageUserGroups(userRoles) 
                ? "Click 'New Group' to create your first user group"
                : "Contact your administrator to create user groups"
              }
            </Text>
          </Box>
        ) : (
          // User Groups Table
          <TableContainer>
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Group Name</Th>
                  <Th>Description</Th>
                  <Th>Members</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {userGroups.map((group) => (
                  <Tr key={group.id} _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}>
                    <Td fontWeight="medium">
                      {group.name}
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor} noOfLines={1}>
                        {group.description || 'No description'}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm">
                        {group.memberCount || 0} users
                      </Text>
                    </Td>
                    <Td>
                      <Badge 
                        size="sm" 
                        colorScheme={group.isActive ? 'green' : 'gray'}
                      >
                        {group.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor}>
                        {group.createdAt || 'recently'}
                      </Text>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Button
                          size="xs"
                          leftIcon={<ViewIcon />}
                          colorScheme="blue"
                          variant="outline"
                          onClick={() => handleViewGroup(group)}
                        >
                          View
                        </Button>
                        
                        {canManageUserGroups(userRoles) && (
                          <>
                            <Button
                              size="xs"
                              leftIcon={<SettingsIcon />}
                              colorScheme="orange"
                              variant="outline"
                              onClick={() => handleManageUsers(group)}
                            >
                              Users
                            </Button>
                            
                            <Menu>
                              <MenuButton
                                as={IconButton}
                                size="xs"
                                icon={<ChevronDownIcon />}
                                variant="outline"
                                colorScheme="gray"
                              />
                              <MenuList>
                                <MenuItem 
                                  icon={<EditIcon />}
                                  onClick={() => handleEditGroup(group)}
                                >
                                  Edit Group
                                </MenuItem>
                                {isAdmin(userRoles) && (
                                  <MenuItem 
                                    icon={<DeleteIcon />}
                                    onClick={() => handleDeleteGroup(group)}
                                    color="red.500"
                                  >
                                    Delete Group
                                  </MenuItem>
                                )}
                              </MenuList>
                            </Menu>
                          </>
                        )}
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