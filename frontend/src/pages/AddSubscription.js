import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  Heading,
  Alert,
  AlertIcon,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormHelperText,
  Switch,
  HStack,
  Text,
  useToast,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { subscriptionsAPI } from '../services/api';

const AddSubscription = () => {
  // Get today's date in YYYY-MM-DD format for the default start date
  const today = new Date().toISOString().split('T')[0];

  const [formData, setFormData] = useState({
    service_name: '',
    subscription_type: 'PAID',
    price: '',
    billing_cycle: 'MONTHLY',
    start_date: today,
    status: 'ACTIVE',
    category: 'OTHER',
    management_link: '',
    send_reminder: false,
    reminder_time: 'SAME_DAY',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();
  const toast = useToast();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePriceChange = (value) => {
    setFormData(prev => ({ ...prev, price: value }));
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      await subscriptionsAPI.create(formData);
      setSuccess('Subscription added successfully');
      toast({
        title: 'Success',
        description: 'Subscription added successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      // Redirect to dashboard after successful submission
      navigate('/');
    } catch (error) {
      setError('Failed to add subscription: ' + (error.response?.data?.detail || error.message));
      toast({
        title: 'Error',
        description: 'Failed to add subscription',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box maxW="container.md" mx="auto" py={8} px={4}>
      <Box bg="white" p={8} borderRadius="lg" shadow="sm">
        <VStack spacing={8} align="stretch">
          <Heading size="lg">Add New Subscription</Heading>

          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              {success}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <VStack spacing={6} align="stretch">
              <FormControl isRequired>
                <FormLabel>Service Name</FormLabel>
                <Input
                  name="service_name"
                  value={formData.service_name}
                  onChange={handleChange}
                  placeholder="e.g., Netflix, Spotify"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Subscription Type</FormLabel>
                <Select
                  name="subscription_type"
                  value={formData.subscription_type}
                  onChange={handleChange}
                >
                  <option value="PAID">Paid</option>
                  <option value="FREE">Free</option>
                </Select>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Price</FormLabel>
                <NumberInput
                  min={0}
                  precision={2}
                  value={formData.price}
                  onChange={handlePriceChange}
                >
                  <NumberInputField placeholder="Enter amount" />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <FormHelperText>Enter the subscription price</FormHelperText>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Billing Cycle</FormLabel>
                <Select
                  name="billing_cycle"
                  value={formData.billing_cycle}
                  onChange={handleChange}
                >
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                  <option value="YEARLY">Yearly</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Start Date</FormLabel>
                <Input
                  name="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={handleChange}
                />
                <FormHelperText>When did this subscription start? Default is today.</FormHelperText>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Category</FormLabel>
                <Select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                >
                  <option value="STREAMING">Streaming</option>
                  <option value="MUSIC">Music</option>
                  <option value="SOFTWARE">Software</option>
                  <option value="OTHER">Other</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Management Link</FormLabel>
                <Input
                  name="management_link"
                  type="url"
                  value={formData.management_link}
                  onChange={handleChange}
                  placeholder="https://"
                />
                <FormHelperText>URL to manage this subscription</FormHelperText>
              </FormControl>

              <FormControl>
                <FormLabel>Reminder Settings</FormLabel>
                <HStack>
                  <Switch 
                    name="send_reminder" 
                    isChecked={formData.send_reminder}
                    onChange={handleSwitchChange}
                  />
                  <Text>Send email reminders</Text>
                </HStack>
              </FormControl>

              {formData.send_reminder && (
                <FormControl>
                  <FormLabel>Reminder Time</FormLabel>
                  <Select
                    name="reminder_time"
                    value={formData.reminder_time}
                    onChange={handleChange}
                  >
                    <option value="SAME_DAY">On the morning of due date</option>
                    <option value="ONE_DAY">1 day ahead</option>
                    <option value="TWO_DAYS">2 days ahead</option>
                    <option value="THREE_DAYS">3 days ahead</option>
                    <option value="ONE_WEEK">1 week ahead</option>
                  </Select>
                </FormControl>
              )}

              <Button
                type="submit"
                colorScheme="purple"
                size="lg"
                isLoading={isLoading}
                mt={4}
              >
                Add Subscription
              </Button>
            </VStack>
          </form>
        </VStack>
      </Box>
    </Box>
  );
};

export default AddSubscription; 