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
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatGroup,
  Alert,
  AlertIcon,
  AlertTitle,
} from '@chakra-ui/react';
import { AddIcon, ArrowBackIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import SubscriptionCard from '../components/SubscriptionCard';
import { subscriptionsAPI } from '../services/api';
import { mockSubscriptions } from '../mockData'; // Fallback for development

const Dashboard = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('next_charge_date');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSubscriptions = async () => {
      try {
        setIsLoading(true);
        
        // Try to fetch from API, fall back to mock data if API fails
        try {
          const response = await subscriptionsAPI.getActive();
          console.log('Getting active subscriptions:', response);
          setSubscriptions(response.data);
        } catch (apiError) {
          console.error('API error, using mock data:', apiError);
          // Fall back to mock data for development
          setSubscriptions(mockSubscriptions);
        }
        
        setIsLoading(false);
      } catch (error) {
        setError('Failed to load subscriptions');
        setIsLoading(false);
      }
    };

    fetchSubscriptions();
  }, []);

  const handleCancel = async (id) => {
    try {
      // Try to call the API
      try {
        await subscriptionsAPI.cancel(id);
      } catch (apiError) {
        console.error('API error when canceling:', apiError);
      }
      
      // Update UI regardless of API success (for development)
      setSubscriptions(subscriptions.filter(sub => sub.id !== id));
    } catch (error) {
      setError('Failed to cancel subscription');
    }
  };

  const handleAddSubscription = () => {
    navigate('/add');
  };

  const filteredSubscriptions = subscriptions
    .filter(sub => !filter || sub.category === filter)
    .sort((a, b) => {
      if (sortBy === 'price') return a.price - b.price;
      if (sortBy === 'name') return a.service_name.localeCompare(b.service_name);
      return new Date(a.next_charge_date) - new Date(b.next_charge_date);
    });

  // Calculate total monthly cost
  const totalMonthlyCost = subscriptions.reduce((total, sub) => {
    if (sub.billing_cycle === 'MONTHLY') {
      return total + parseFloat(sub.price);
    } else if (sub.billing_cycle === 'YEARLY') {
      return total + (parseFloat(sub.price) / 12);
    }
    return total;
  }, 0);

  // Calculate total yearly cost
  const totalYearlyCost = subscriptions.reduce((total, sub) => {
    if (sub.billing_cycle === 'MONTHLY') {
      return total + (parseFloat(sub.price) * 12);
    } else if (sub.billing_cycle === 'YEARLY') {
      return total + parseFloat(sub.price);
    } else if (sub.billing_cycle === 'WEEKLY') {
      return total + (parseFloat(sub.price) * 52);
    }
    return total;
  }, 0);

  return (
    <Box maxW="container.xl" mx="auto" py={8} px={4}>
      <VStack spacing={8} align="stretch">
        <Flex justify="space-between" align="center">
          <Heading size="lg">Active Subscriptions</Heading>
          <HStack spacing={4}>
            <Button
              colorScheme="gray"
              onClick={() => navigate('/cancelled')}
            >
              View Cancelled
            </Button>
            <Button
              leftIcon={<AddIcon />}
              colorScheme="purple"
              onClick={handleAddSubscription}
            >
              Add Subscription
            </Button>
          </HStack>
        </Flex>

        {/* Stats Section */}
        <StatGroup bg="white" p={4} borderRadius="lg" shadow="sm">
          <Stat>
            <StatLabel>Monthly Spending</StatLabel>
            <StatNumber>${totalMonthlyCost.toFixed(2)}</StatNumber>
            <StatHelpText>All active subscriptions</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Yearly Spending</StatLabel>
            <StatNumber>${totalYearlyCost.toFixed(2)}</StatNumber>
            <StatHelpText>Projected annual cost</StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Total Subscriptions</StatLabel>
            <StatNumber>{subscriptions.length}</StatNumber>
            <StatHelpText>Active services</StatHelpText>
          </Stat>
        </StatGroup>

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
            <option value="next_charge_date">Next Charge Date</option>
            <option value="price">Price</option>
            <option value="name">Name</option>
          </Select>
        </HStack>

        {isLoading ? (
          <Text>Loading subscriptions...</Text>
        ) : error ? (
          <Alert status="error">
            <AlertIcon />
            <AlertTitle>{error}</AlertTitle>
          </Alert>
        ) : filteredSubscriptions.length === 0 ? (
          <Alert status="info">
            <AlertIcon />
            <AlertTitle>No subscriptions found</AlertTitle>
          </Alert>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {filteredSubscriptions.map((subscription) => (
              <SubscriptionCard
                key={subscription.id}
                subscription={subscription}
                onCancel={handleCancel}
              />
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  );
};

export default Dashboard; 