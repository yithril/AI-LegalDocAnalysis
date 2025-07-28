'use client';

import { Box, Flex, Button, Text, useColorModeValue } from '@chakra-ui/react';
import { useRouter } from 'next/navigation';
import Logo from '../Logo';

export default function Navbar() {
  const router = useRouter();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleHomeClick = () => {
    router.push('/dashboard');
  };

  return (
    <Box 
      as="nav" 
      bg={bgColor} 
      borderBottom="1px" 
      borderColor={borderColor}
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Flex 
        maxW="1200px" 
        mx="auto" 
        px={4} 
        py={3}
        align="center"
        justify="space-between"
      >
        {/* Left side - Logo */}
        <Flex align="center">
          <Logo className="h-8" />
        </Flex>

        {/* Center - Menu */}
        <Flex 
          align="center" 
          justify="center" 
          flex={1}
          gap={6}
        >
          <Button
            variant="ghost"
            onClick={handleHomeClick}
            _hover={{ bg: useColorModeValue('gray.100', 'gray.700') }}
          >
            Home
          </Button>
          {/* Future menu items will go here */}
        </Flex>

        {/* Right side - User info/actions */}
        <Flex align="center" gap={4}>
          <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
            Welcome
          </Text>
          {/* Future user menu will go here */}
        </Flex>
      </Flex>
    </Box>
  );
} 