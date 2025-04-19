import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  Button,
  HStack,
  VStack,
  Select,
  Text,
  Flex,
  Alert,
  AlertIcon,
  AlertTitle,
  useToast,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
} from '@chakra-ui/react';
import { ArrowBackIcon, DeleteIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import SubscriptionCard from '../components/SubscriptionCard';
import { subscriptionsAPI } from '../services/api';

const CancelledSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('cancellation_date');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  const fetchCancelledSubscriptions = async () => {
    try {
      setIsLoading(true);
      const response = await subscriptionsAPI.getCancelled();
      setSubscriptions(response.data.cancelled_subscriptions);
      setIsLoading(false);
    } catch (error) {
      setError('Failed to load cancelled subscriptions');
      setIsLoading(false);
      toast({
        title: 'Error',
        description: 'Failed to load cancelled subscriptions',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  useEffect(() => {
    fetchCancelledSubscriptions();
  }, []);

  const filteredSubscriptions = subscriptions
    .filter(sub => !filter || sub.category === filter)
    .sort((a, b) => {
      if (sortBy === 'name') return a.service_name.localeCompare(b.service_name);
      // Sort by cancellation date (most recent first)
      return new Date(b.cancellation_date) - new Date(a.cancellation_date);
    });

  const handleRestore = (subscription) => {
    navigate(`/edit/${subscription.id}`, {
      state: { 
        subscription: {
          ...subscription,
          status: 'ACTIVE',
          cancellation_date: null
        },
        fromCancelled: true
      }
    });
  };

  const handleDelete = async (id) => {
    try {
      await subscriptionsAPI.delete(id);
      // Refresh the cancelled subscriptions list
      fetchCancelledSubscriptions();
      toast({
        title: 'Success',
        description: 'Subscription removed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to remove subscription',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDeleteAll = async () => {
    try {
      // Assuming you have an API endpoint for this
      await subscriptionsAPI.deleteAllCancelled();
      fetchCancelledSubscriptions();
      onClose();
      toast({
        title: 'Success',
        description: 'All cancelled subscriptions removed',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to remove subscriptions',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box maxW="container.xl" mx="auto" py={8} px={4}>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>Cancelled Subscriptions</Heading>
        <Button
          leftIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
        >
          Back to Dashboard
        </Button>
      </Flex>

      <Flex justify="space-between" align="center" mb={6}>
        <HStack spacing={4}>
          <Select
            placeholder="Filter by category"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            bg="white"
            w={{ base: "full", md: "200px" }}
          >
            <option value="STREAMING">Streaming</option>
            <option value="MUSIC">Music</option>
            <option value="SOFTWARE">Software</option>
            <option value="OTHER">Other</option>
          </Select>

          <Select
            placeholder="Sort by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            bg="white"
            w={{ base: "full", md: "200px" }}
          >
            <option value="cancellation_date">Cancellation Date</option>
            <option value="name">Name</option>
          </Select>
        </HStack>
        
        <Button
          colorScheme="red"
          variant="ghost"
          leftIcon={<DeleteIcon />}
          onClick={onOpen}
        >
          Remove All
        </Button>
      </Flex>

      {isLoading ? (
        <Text>Loading cancelled subscriptions...</Text>
      ) : error ? (
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      ) : filteredSubscriptions.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          <AlertTitle>No cancelled subscriptions found</AlertTitle>
        </Alert>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {filteredSubscriptions.map((subscription) => (
            <SubscriptionCard
              key={subscription.id}
              subscription={subscription}
              isCancelled={true}
              onRestore={() => handleRestore(subscription)}
              onDelete={handleDelete}
            />
          ))}
        </SimpleGrid>
      )}

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Remove All Subscriptions</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={2} align="stretch">
              <Text>Are you removing all cancelled subscriptions?</Text>
              <Text fontSize="sm" color="red.500">
                Cannot restore them after removing
              </Text>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              No, Keep Them
            </Button>
            <Button colorScheme="red" onClick={handleDeleteAll}>
              Yes, Remove All
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default CancelledSubscriptions; 