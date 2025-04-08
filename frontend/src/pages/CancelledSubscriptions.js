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
} from '@chakra-ui/react';
import { ArrowBackIcon } from '@chakra-ui/icons';
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

  useEffect(() => {
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

    fetchCancelledSubscriptions();
  }, [toast]);

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

  return (
    <Box maxW="container.xl" mx="auto" py={8} px={4}>
      <VStack spacing={8} align="stretch">
        <Flex justify="space-between" align="center">
          <Heading size="lg">Cancelled Subscriptions</Heading>
          <Button
            leftIcon={<ArrowBackIcon />}
            colorScheme="gray"
            onClick={() => navigate('/')}
          >
            Back to Dashboard
          </Button>
        </Flex>

        {/* Filters */}
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
                showEditButton={false}
              />
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  );
};

export default CancelledSubscriptions; 