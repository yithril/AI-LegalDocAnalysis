'use client';

import { 
  Box, 
  VStack, 
  Heading, 
  Text, 
  Badge, 
  Flex, 
  useColorModeValue,
  Icon,
  HStack
} from '@chakra-ui/react';

export default function NotificationsBox({ notifications = [] }) {
  const boxBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock notifications for now
  const mockNotifications = [
    {
      id: 1,
      type: 'info',
      message: 'New user "John Doe" joined the system',
      time: '2 minutes ago',
      read: false
    },
    {
      id: 2,
      type: 'success',
      message: 'Project "Legal Review 2024" was created successfully',
      time: '1 hour ago',
      read: true
    },
    {
      id: 3,
      type: 'warning',
      message: 'Document "Contract_v2.pdf" needs approval',
      time: '3 hours ago',
      read: false
    },
    {
      id: 4,
      type: 'info',
      message: 'User group "Analysts" was updated',
      time: '1 day ago',
      read: true
    }
  ];

  const notificationsToShow = notifications.length > 0 ? notifications : mockNotifications;

  const getBadgeColor = (type) => {
    switch (type) {
      case 'success': return 'green';
      case 'warning': return 'orange';
      case 'error': return 'red';
      default: return 'blue';
    }
  };

  return (
    <Box 
      bg={boxBg} 
      border="1px" 
      borderColor={borderColor} 
      borderRadius="lg" 
      p={6}
      h="400px"
      overflowY="auto"
    >
      <VStack spacing={4} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Heading size="md">Notifications</Heading>
          <Badge colorScheme="blue" variant="subtle">
            {notificationsToShow.filter(n => !n.read).length} new
          </Badge>
        </Flex>
        
        {/* Notifications List */}
        <VStack spacing={3} align="stretch">
          {notificationsToShow.map((notification) => (
            <Box 
              key={notification.id}
              p={3}
              bg={notification.read ? 'transparent' : useColorModeValue('blue.50', 'blue.900')}
              borderRadius="md"
              borderLeft="3px solid"
              borderLeftColor={getBadgeColor(notification.type)}
            >
              <Flex justify="space-between" align="start">
                <Box flex={1}>
                  <Text fontSize="sm" fontWeight={notification.read ? 'normal' : 'medium'}>
                    {notification.message}
                  </Text>
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    {notification.time}
                  </Text>
                </Box>
                <Badge 
                  colorScheme={getBadgeColor(notification.type)} 
                  size="sm"
                  ml={2}
                >
                  {notification.type}
                </Badge>
              </Flex>
            </Box>
          ))}
        </VStack>
        
        {/* Empty State */}
        {notificationsToShow.length === 0 && (
          <Box textAlign="center" py={8}>
            <Text color="gray.500">No notifications</Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
} 