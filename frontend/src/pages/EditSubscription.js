import React, { useState, useEffect } from 'react';
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
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { subscriptionsAPI } from '../services/api';

const EditSubscription = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  
  // Check if we came from the cancelled page
  const cameFromCancelled = location.state?.fromCancelled === true;

  // Update initialData with default reminder values
  const initialData = {
    service_name: '',
    subscription_type: 'PAID',
    price: '',
    billing_cycle: 'MONTHLY',
    start_date: '',
    status: 'ACTIVE',
    category: 'OTHER',
    management_link: '',
    send_reminder: false,
    reminder_days_ahead: 1,
    reminder_hour: 9,
    reminder_minute: 0,
    reminder_ampm: 'AM',
  };
  
  const [formData, setFormData] = useState(
    location.state?.subscription || initialData
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Update useEffect to properly set the reminder values
  useEffect(() => {
    if (!location.state?.subscription && id) {
      const fetchSubscription = async () => {
        try {
          setIsLoading(true);
          const response = await subscriptionsAPI.getById(id);
          const subscriptionData = response.data;
          
          // Ensure reminder settings are properly set from existing data
          setFormData({
            ...subscriptionData,
            reminder_days_ahead: subscriptionData.reminder_days_ahead || 1,
            reminder_hour: subscriptionData.reminder_hour || 9,
            reminder_minute: subscriptionData.reminder_minute || 0,
            reminder_ampm: subscriptionData.reminder_ampm || 'AM',
            send_reminder: Boolean(subscriptionData.send_reminder)
          });
        } catch (error) {
          setError('Failed to fetch subscription details');
          toast({
            title: 'Error',
            description: 'Failed to fetch subscription details',
            status: 'error',
            duration: 3000,
            isClosable: true,
          });
        } finally {
          setIsLoading(false);
        }
      };

      fetchSubscription();
    }
  }, [id, location.state, toast]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePriceChange = (value) => {
    setFormData(prev => ({ ...prev, price: value }));
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked,
      // Only set default values if there are no existing values
      ...(name === 'send_reminder' && checked && !prev.reminder_days_ahead ? {
        reminder_days_ahead: 1,
        reminder_hour: 9,
        reminder_minute: 0,
        reminder_ampm: 'AM'
      } : {})
    }));
  };

  const handleTimeChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      await subscriptionsAPI.update(id, formData);
      setSuccess('Subscription updated successfully');
      toast({
        title: 'Success',
        description: 'Subscription updated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      // Redirect to dashboard after successful update
      navigate('/');
    } catch (error) {
      setError('Failed to update subscription: ' + (error.response?.data?.detail || error.message));
      toast({
        title: 'Error',
        description: 'Failed to update subscription',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelClick = () => {
    // Navigate back based on where the user came from
    if (cameFromCancelled) {
      navigate('/cancelled'); 
    } else {
      navigate('/'); // Default back to dashboard
    }
  };

  return (
    <Box maxW="container.md" mx="auto" py={8} px={4}>
      <Box bg="white" p={8} borderRadius="lg" shadow="sm">
        <VStack spacing={8} align="stretch">
          <Heading size="lg">Edit Subscription</Heading>

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
                  <option value="FREE_TRIAL">Free Trial</option>
                </Select>
              </FormControl>

              <FormControl isRequired={formData.subscription_type === 'PAID'}>
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
                <FormHelperText>
                  {formData.subscription_type === 'PAID' ? 'Enter the subscription price' : 'Price is optional for Free Trial'}
                </FormHelperText>
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
                  value={formData.start_date ? formData.start_date.split('T')[0] : ''}
                  onChange={handleChange}
                />
                <FormHelperText>When did this subscription start?</FormHelperText>
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
                  value={formData.management_link || ''}
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
                <>
                  <FormControl>
                    <FormLabel>Days Ahead for Reminder</FormLabel>
                    <NumberInput
                      min={1}
                      max={formData.subscription_type === 'FREE_TRIAL' ? formData.free_trial_length : undefined}
                      value={formData.reminder_days_ahead}
                      onChange={(value) => setFormData({ ...formData, reminder_days_ahead: value })}
                    >
                      <NumberInputField placeholder="Enter number of days" />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                    <FormHelperText>Set how many days ahead of the due date to send the reminder.</FormHelperText>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Reminder Time</FormLabel>
                    <HStack>
                      <NumberInput
                        min={1}
                        max={12}
                        value={formData.reminder_hour}
                        defaultValue={formData.reminder_hour}
                        onChange={(value) => handleTimeChange('reminder_hour', value)}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                      <Text>:</Text>
                      <NumberInput
                        min={0}
                        max={59}
                        value={formData.reminder_minute}
                        onChange={(value) => handleTimeChange('reminder_minute', value)}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                      <Select
                        name="reminder_ampm"
                        value={formData.reminder_ampm}
                        onChange={handleChange}
                      >
                        <option value="AM">AM</option>
                        <option value="PM">PM</option>
                      </Select>
                    </HStack>
                    <FormHelperText>Select the reminder time (12-hour format).</FormHelperText>
                  </FormControl>
                </>
              )}

              <HStack spacing={4} justify="flex-end">
                <Button
                  variant="outline"
                  onClick={handleCancelClick}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  colorScheme="purple"
                  isLoading={isLoading}
                >
                  Save Changes
                </Button>
              </HStack>
            </VStack>
          </form>
        </VStack>
      </Box>
    </Box>
  );
};

export default EditSubscription; 