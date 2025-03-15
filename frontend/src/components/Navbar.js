import React from 'react';
import { Box, Flex, Button, Heading, Spacer, HStack } from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <Box as="nav" bg="purple.600" color="white" py={4} px={8} shadow="md">
      <Flex align="center" maxW="container.xl" mx="auto">
        <Heading size="md" as={RouterLink} to="/" _hover={{ textDecoration: 'none' }}>
          Subscription Manager
        </Heading>
        <Spacer />
        {isAuthenticated ? (
          <HStack spacing={4}>
            <Button as={RouterLink} to="/" variant="ghost" colorScheme="whiteAlpha">
              Dashboard
            </Button>
            <Button as={RouterLink} to="/add" variant="ghost" colorScheme="whiteAlpha">
              Add Subscription
            </Button>
            <Button 
              variant="outline" 
              colorScheme="whiteAlpha"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </HStack>
        ) : (
          <Flex gap={4}>
            <Button as={RouterLink} to="/login" variant="ghost" colorScheme="whiteAlpha">
              Login
            </Button>
            <Button as={RouterLink} to="/register" variant="solid" colorScheme="whiteAlpha">
              Register
            </Button>
          </Flex>
        )}
      </Flex>
    </Box>
  );
};

export default Navbar; 