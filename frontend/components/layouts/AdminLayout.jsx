'use client';

import { Box, Flex, VStack, Heading, Text, useColorModeValue } from '@chakra-ui/react';
import Navbar from './Navbar';

export default function AdminLayout({ 
  children, 
  sidebarContent,
  title = "Admin Dashboard",
  subtitle = "Manage projects and user groups"
}) {
  const sidebarBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const mainBg = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box minH="100vh" bg={mainBg}>
      {/* Navigation */}
      <Navbar />
      
      {/* Main Layout */}
      <Flex h="calc(100vh - 64px)">
        {/* Left Sidebar - Projects */}
        <Box 
          w="400px" 
          bg={sidebarBg} 
          borderRight="1px" 
          borderColor={borderColor}
          p={6}
          overflowY="auto"
        >
          <VStack spacing={6} align="stretch">
            {/* Sidebar Header */}
            <Box>
              <Heading size="md" mb={2}>
                Projects
              </Heading>
              <Text fontSize="sm" color="gray.500">
                Select a project to manage
              </Text>
            </Box>
            
            {/* Sidebar Content */}
            <Box flex={1}>
              {sidebarContent}
            </Box>
          </VStack>
        </Box>
        
        {/* Main Content Area */}
        <Box flex={1} p={6} overflowY="auto">
          <VStack spacing={6} align="stretch">
            {/* Page Header */}
            <Box>
              <Heading size="lg" mb={2}>
                {title}
              </Heading>
              <Text color="gray.600">
                {subtitle}
              </Text>
            </Box>
            
            {/* Main Content */}
            <Box>
              {children}
            </Box>
          </VStack>
        </Box>
      </Flex>
    </Box>
  );
} 