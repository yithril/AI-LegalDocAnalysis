'use client';

import { Box, Container, Heading, Text, VStack } from '@chakra-ui/react';
import Navbar from './Navbar';

export default function SimpleLayout({ children, title = "Projects", subtitle = "Select a project to view documents" }) {
  return (
    <Box minH="100vh" bg="gray.50">
      {/* Navigation */}
      <Navbar />
      
      {/* Main Content */}
      <Container maxW="1200px" py={8}>
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
          
          {/* Content Area */}
          <Box>
            {children}
          </Box>
        </VStack>
      </Container>
    </Box>
  );
} 